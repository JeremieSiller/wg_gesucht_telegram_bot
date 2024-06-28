import functools
import logging

import requests
import telegram
from telegram import ext as t_ext

from app import config, id_shelve
from app.crawlers import wg_gesucht_crawler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def job(
    context: t_ext.ContextTypes.DEFAULT_TYPE,
    id_store: id_shelve.MappingIdShelve,
    link_store: id_shelve.MappingLinkShelve,
) -> None:
    assert context.job is not None
    assert context.job.chat_id is not None
    chat_id: int = context.job.chat_id
    logging.info(f"Reading base_url from for chatd_id: {chat_id}")
    url = link_store.read_link(str(chat_id))
    logging.info(f"Loading data for url: {url}")

    crawler = wg_gesucht_crawler.WgGesuchtCrawler(link_store.read_link(str(chat_id)))
    ad_data = crawler.crawl_offers()
    new_ids = [item.id for item in ad_data]
    old_ids = id_store.read_used_ids(f"{chat_id}")

    unused_ids = list(set(new_ids) - set(old_ids))
    logging.info(f"Found ads with new ids: {unused_ids}")
    if not unused_ids:
        return
    messages = [
        f'{item.title + "\n" if item.title else ""}'
        f'{"Price: " + str(item.price) + "€\n" if item.price else ""}'
        f'{"Available from: " + item.beginning.strftime("%d-%m-%Y") + "\n" if item.beginning else ""}'
        f'{"Available until: " + item.until.strftime("%d-%m-%Y") + "\n" if item.until else ""}'
        f'{"Uploaded: " + item.upload_string + "\n" if item.upload_string else ""}'
        f"{item.link}\n"
        for item in ad_data
        if item.id in unused_ids
    ]
    if not messages:
        return

    for message in reversed(messages):
        logging.info(f"Sending message: '{message}' to {chat_id}")
        await context.bot.send_message(chat_id, message)  # type: ignore
    id_store.store_used_ids(str(chat_id), list(set(new_ids + old_ids)))


async def start(
    update: telegram.Update,
    context: t_ext.ContextTypes.DEFAULT_TYPE,
    id_store: id_shelve.MappingIdShelve,
    link_store: id_shelve.MappingLinkShelve,
) -> None:
    partial_job = functools.partial(job, id_store=id_store, link_store=link_store)
    partial_job.__name__ = "partial_job"  # type: ignore
    chat_id: int = update.effective_chat.id  # type: ignore

    if id_store.is_chat_id_already_in_keys(chat_id):
        logging.info(f"{chat_id} tried to register again, returning")
        await context.bot.send_message(
            chat_id,
            text="You are already registered",
        )
        return

    args = update.message.text.split(" ")  # type: ignore
    if len(args) != 2:
        logging.info(f"Arguments passed: {args}")
        await context.bot.send_message(
            chat_id,
            text="You need to pass exactly one argument, the url to the wg-gesucht search page",
        )
        return
    res = requests.get(args[1])
    if res.status_code != 200:
        logging.info(f"Url not reachable: {args[1]}")
        await context.bot.send_message(
            chat_id,
            text="The url you provided is not reachable",
        )
        return

    id_store.store_used_ids(str(chat_id), [])
    link_store.store_link(str(chat_id), args[1])

    logging.info(f"New job registered for {update.effective_chat.id}")  # type: ignore
    await context.bot.send_message(
        chat_id,
        text="You successully registered for the wg_gesucht bot",
    )
    context.job_queue.run_repeating(  # type: ignore
        partial_job, interval=10, first=0, chat_id=chat_id
    )


async def help_command(
    update: telegram.Update, context: t_ext.ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id  # type: ignore
    await context.bot.send_message(
        chat_id,
        text="You can register for the bot by sending /start <url> where url is the wg-gesucht search page\n"
        + "To apply filters just add them on the wg-gesucht search page and copy the full url\n",
    )


def _register_existing_chat_id_jobs(
    application: t_ext.Application,
    id_store: id_shelve.MappingIdShelve,
    link_store: id_shelve.MappingLinkShelve,
) -> None:
    chat_id_strings = id_store.get_chat_ids()
    chat_ids = set([s.split("|")[-1] for s in chat_id_strings])
    partial_job = functools.partial(job, id_store=id_store, link_store=link_store)
    partial_job.__name__ = "partial_job"  # type: ignore
    for chat_id in chat_ids:
        application.job_queue.run_repeating(  # type: ignore
            partial_job, interval=10, first=0, chat_id=int(chat_id)
        )


def main() -> None:
    logging.info("starting telegram bot")
    application = (
        t_ext.Application.builder().token(config.settings.telegram_token).build()
    )
    id_store = id_shelve.MappingIdShelve(config.settings.ids_file_name)
    link_store = id_shelve.MappingLinkShelve(config.settings.links_file_name)

    _register_existing_chat_id_jobs(application, id_store, link_store=link_store)

    partial_start = functools.partial(start, id_store=id_store, link_store=link_store)
    application.add_handler(t_ext.CommandHandler(["start"], partial_start))
    application.add_handler(t_ext.CommandHandler(["help"], help_command))
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)


if __name__ == "__main__":
    main()
