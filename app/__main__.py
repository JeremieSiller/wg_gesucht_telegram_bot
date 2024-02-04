import functools
import logging

import telegram
from telegram import ext as t_ext

from app import config, id_shelve
from app.crawlers import asbtract_crawler, kleinanzeigen_crawler, wg_gesucht_crawler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

crawlers: list[asbtract_crawler.Crawler] = []


async def job(
    context: t_ext.ContextTypes.DEFAULT_TYPE, id_store: id_shelve.MappingIdShelve
) -> None:
    logging.info(f"Loading base_url {config.settings.kleinanzeigen_url}")
    chat_id: int = context.job.chat_id  # type: ignore

    for crawler in crawlers:
        ad_data = crawler.crawl_offers()
        new_ids = [item.id for item in ad_data]
        old_ids = id_store.read_used_ids(f"{crawler.name}|{chat_id}")

        unused_ids = list(set(new_ids) - set(old_ids))
        logging.info(f"Found ads with new ids: {unused_ids}")
        if not unused_ids:
            continue

        strings = [
            f"{item.title + '\n' if item.title else ''}"
            f"{item.price}\n"
            f"{item.link}\n"
            for item in ad_data
            if item.id in unused_ids and item.price < config.settings.max_price
        ]
        message = "\n".join(strings)
        if not message:
            continue

        logging.info(f"Sending message: '{message}' to {chat_id}")
        await context.bot.send_message(chat_id, message)  # type: ignore
        id_store.store_used_ids(
            f"{crawler.name}|{chat_id}", list(set(new_ids + old_ids))
        )


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
    chat_id_strings = id_store.get_chat_ids()
    chat_ids = set([s.split("|")[-1] for s in chat_id_strings])
    partial_job = functools.partial(job, id_store=id_store)
    partial_job.__name__ = "partial_job"  # type: ignore
    for chat_id in chat_ids:
        application.job_queue.run_repeating(  # type: ignore
            partial_job, interval=10, first=0, chat_id=int(chat_id)
        )


def setup_crawlers() -> None:
    global crawlers
    crawlers.append(
        kleinanzeigen_crawler.KleinanzeigenCrawler(config.settings.kleinanzeigen_url)
    )
    crawlers.append(wg_gesucht_crawler.WgGesuchtCrawler(config.settings.wg_gesucht_url))


def main() -> None:
    logging.info("starting job")

    application = (
        t_ext.Application.builder().token(config.settings.telegram_token).build()
    )
    id_store = id_shelve.MappingIdShelve(config.settings.ids_file_name)
    setup_crawlers()

    _register_existing_chat_id_jobs(application, id_store)

    partial_start = functools.partial(start, id_store=id_store)
    application.add_handler(t_ext.CommandHandler(["start"], partial_start))
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)


if __name__ == "__main__":
    main()
