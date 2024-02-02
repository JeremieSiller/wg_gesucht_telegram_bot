import functools
import logging
from dataclasses import dataclass
from urllib import parse as url_parse

import bs4
import httpx
import telegram
from telegram import ext as t_ext

from wohnungs_bot import config, id_shelve

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

base_url = url_parse.urlparse(config.settings.kleinanzeigen_url).netloc


@dataclass
class AdData:
    id: str
    ref: str
    price: int


def _convert_price_to_int(price_string: str) -> int:
    stripped_string = price_string.strip()
    no_currency = stripped_string.replace("€", "").strip()

    no_seperator = no_currency.replace(".", "")
    try:
        return int(no_seperator)
    except ValueError:
        return 0


def _get_add_data() -> list[AdData]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    }
    with httpx.Client(http2=True) as client:
        result = client.get(config.settings.kleinanzeigen_url, headers=headers)

    soup = bs4.BeautifulSoup(result.text, "lxml")
    ads = soup.find_all("article", {"class": "aditem"})

    data_list = []
    for ad in ads:
        sub_soup = bs4.BeautifulSoup(str(ad))
        price = sub_soup.find(
            "p", {"class": "aditem-main--middle--price-shipping--price"}
        )
        price_as_int = _convert_price_to_int(price.text)
        data_list.append(
            AdData(
                id=ad["data-adid"],
                ref=ad["data-href"],
                price=price_as_int,
            )
        )

    return data_list


async def job(
    context: t_ext.ContextTypes.DEFAULT_TYPE, id_store: id_shelve.MappingIdShelve
) -> None:
    logging.info(f"Loading base_url {config.settings.kleinanzeigen_url}")
    chat_id: int = context.job.chat_id  # type: ignore

    ad_data = _get_add_data()
    new_ids = [item.id for item in ad_data]
    old_ids = id_store.read_used_ids(chat_id)

    unused_ids = list(set(new_ids) - set(old_ids))
    logging.info(f"Found ads with new ids: {unused_ids}")
    if not unused_ids:
        return

    strings = [
        f"{base_url}{item.ref}\n"
        for item in ad_data
        if item.id in unused_ids and item.price < config.settings.max_price
    ]
    message = "\n".join(strings)

    logging.info(f"Sending message: '{message}' to {chat_id}")
    await context.bot.send_message(chat_id, message)  # type: ignore
    id_store.store_used_ids(chat_id, list(set(new_ids + old_ids)))


async def start(
    update: telegram.Update,
    context: t_ext.ContextTypes.DEFAULT_TYPE,
) -> None:
    id_store = id_shelve.MappingIdShelve("ids")

    partial_job = functools.partial(job, id_store=id_store)
    partial_job.__name__ = "partial_job"  # type: ignore
    logging.info(f"New job registered for {update.effective_chat.id}")  # type: ignore
    await context.bot.send_message(
        update.effective_chat.id,  # type: ignore
        text="You successully registered for the kleinanzeigen bot",
    )
    context.job_queue.run_repeating(  # type: ignore
        partial_job, interval=10, first=0, chat_id=update.effective_message.chat_id  # type: ignore
    )


def main() -> None:
    logging.info("starting job")

    application = (
        t_ext.Application.builder().token(config.settings.telegram_token).build()
    )

    application.add_handler(t_ext.CommandHandler(["start"], start))

    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)


if __name__ == "__main__":
    main()
