import functools
import logging
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


def _get_current_ids_and_urls() -> list[tuple[str, str]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    }
    with httpx.Client(http2=True) as client:
        result = client.get(config.settings.kleinanzeigen_url, headers=headers)

    soup = bs4.BeautifulSoup(result.text, "lxml")
    ads = soup.find_all("article", {"class": "aditem"})
    return [(ad.attrs["data-adid"], ad.attrs["data-href"]) for ad in ads]


async def job(
    context: t_ext.ContextTypes.DEFAULT_TYPE, id_store: id_shelve.MappingIdShelve
) -> None:
    logging.info(f"Loading base_url {config.settings.kleinanzeigen_url}")
    chat_id: int = context.job.chat_id  # type: ignore

    ids_and_links = _get_current_ids_and_urls()
    new_ids = [item[0] for item in ids_and_links]
    old_ids = id_store.read_used_ids(chat_id)

    unused_ids = list(set(new_ids) - set(old_ids))
    logging.info(f"Found ads with new ids: {unused_ids}")
    if not unused_ids:
        return

    strings = [
        f"{base_url}{item[1]}\n" for item in ids_and_links if item[0] in unused_ids
    ]
    message = "\n".join(strings)

    logging.info(f"Sending message: '{message}' to {chat_id}")
    await context.bot.send_message(chat_id, message)  # type: ignore
    id_store.store_used_ids(chat_id, list(set(new_ids + old_ids)))


async def start(
    update: telegram.Update,
    context: t_ext.ContextTypes.DEFAULT_TYPE,
    id_store: id_shelve.MappingIdShelve,
) -> None:
    partial_job = functools.partial(job, id_store=id_store)
    partial_job.__name__ = "partial_job"  # type: ignore
    chat_id: int = update.effective_chat.id  # type: ignore

    if id_store.is_chat_id_already_in_keys(chat_id):
        logging.info(f"{chat_id} tried to register again, returning")
        await context.bot.send_message(
            chat_id,
            text="You are already registered",
        )
        return

    logging.info(f"New job registered for {update.effective_chat.id}")  # type: ignore
    await context.bot.send_message(
        chat_id,
        text="You successully registered for the kleinanzeigen bot",
    )
    context.job_queue.run_repeating(  # type: ignore
        partial_job, interval=10, first=0, chat_id=chat_id
    )


def _register_existing_chat_id_jobs(
    application: t_ext.Application, id_store: id_shelve.MappingIdShelve
) -> None:
    chat_ids = id_store.get_chat_ids()
    partial_job = functools.partial(job, id_store=id_store)
    partial_job.__name__ = "partial_job"  # type: ignore
    for chat_id in chat_ids:
        application.job_queue.run_repeating(  # type: ignore
            partial_job, interval=10, first=0, chat_id=int(chat_id)
        )


def main() -> None:
    logging.info("starting job")

    application = (
        t_ext.Application.builder().token(config.settings.telegram_token).build()
    )
    id_store = id_shelve.MappingIdShelve(config.settings.ids_file_name)
    _register_existing_chat_id_jobs(application, id_store)

    partial_start = functools.partial(start, id_store=id_store)
    application.add_handler(t_ext.CommandHandler(["start"], partial_start))
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)


if __name__ == "__main__":
    main()