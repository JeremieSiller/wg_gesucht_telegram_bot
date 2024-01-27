import functools
import logging

import telegram
from selenium import webdriver
from telegram import ext as t_ext
from webdriver_manager.chrome import ChromeDriverManager

from wohnungs_bot import config, id_shelve, kleinanzeigen_sel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def job(
    context: t_ext.ContextTypes.DEFAULT_TYPE,
    crawler: kleinanzeigen_sel.KleinanzeigenCrawler,
    id_store: id_shelve.IdShelve,
) -> None:
    logging.info(f"Loading base_url {crawler.base_url}")
    crawler.load_base()

    crawler.accept_cookies()

    new_ids = crawler.get_all_ids_on_page()
    old_ids = id_store.read_used_ids()

    unused_ids = list(set(new_ids) - set(old_ids))

    data = crawler.get_data_for_ids(unused_ids)

    strings = [f"{d['title']}\n{d['url']}\n" for d in data]
    message = "\n".join(strings)
    (await context.bot.send_message(context.job.chat_id, message)) if message else None  # type: ignore

    id_store.store_used_ids(list(set(new_ids + old_ids)))


async def start(
    update: telegram.Update,
    context: t_ext.ContextTypes.DEFAULT_TYPE,
    crawler: kleinanzeigen_sel.KleinanzeigenCrawler,
) -> None:
    id_store = id_shelve.IdShelve("ids")

    partial_job = functools.partial(job, crawler=crawler, id_store=id_store)
    partial_job.__name__ = "partial_job"  # type: ignore

    await context.bot.send_message(
        update.effective_chat.id,  # type: ignore
        text="You successully registered for the wohnungs notifier",
    )
    context.job_queue.run_repeating(  # type: ignore
        partial_job, interval=60, first=0, chat_id=update.effective_message.chat_id  # type: ignore
    )


def main() -> None:
    options = webdriver.ChromeOptions()
    path = ChromeDriverManager().install()
    service = webdriver.ChromeService(executable_path=path)
    driver = webdriver.Chrome(options=options, service=service)
    base_url = config.settings.kleinanzeigen_url
    crawler = kleinanzeigen_sel.KleinanzeigenCrawler(base_url=base_url, driver=driver)

    application = (
        t_ext.Application.builder().token(config.settings.telegram_token).build()
    )

    partial_start = functools.partial(start, crawler=crawler)

    application.add_handler(t_ext.CommandHandler(["start"], partial_start))

    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)


if __name__ == "__main__":
    main()
