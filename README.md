# WG Gesucht Bot

This is a bot that scrapes new entries on WG Gesucht and sends notifications via Telegram when there is a new entry. It helps you stay updated on new listings for any search query you want. It is able to serve mutliple users that can subscribe to different search queries.

## Usage

To use this bot, follow these steps:

1. Clone the repository: `git clone https://github.com/JeremieSiller/kleinanzeigen_bot.git`
2. Install the dependencies using [Poetry](https://python-poetry.org/): `poetry install`
3. create `.env` file in the root directory and add the following variables:
```
TELEGRAM_TOKEN=your_telegram_bot_token # check step 5
IDS_FILE_NAME=ids.db
LINK_FILE_NAME=links.db
```
4. Create the files `ids.db` and `links.db` in the root directory:
```
touch ids.db
touch links.db
```
5. Obtain a Telegram Bot token from [BotFather](https://core.telegram.org/bots#botfather) and add it to the `.env` file under `TELEGRAM_TOKEN`.
6. Run the bot: `poetry run python main.py`
7. send `/start` to your bot and it will start scraping the urls you provided and send you a message with the new listings.

- if you want to use certain filters, just add them on wg-gesucht and copy the new url to the `/start` command.

Alternatively, you can use Docker to run the bot:

1. Build the Docker image: `docker build -t telegram-scraper .`
2. Run the Docker container: `docker run telegram-scraper`

## License

This project is licensed under the [MIT License](LICENSE).

## Miscellaneous

This project was created as a learning experience and is not intended for production use. It is not affiliated with Kleinanzeigen or WG Gesucht.

## TODO:
- add kleinanzeigen (and other webpages)
- use actual database instead of shelve
- handle race conditions properly
- write tests

## Additional Resources

- [Poetry](https://python-poetry.org/): A dependency management and packaging tool for Python.
- [BotFather](https://core.telegram.org/bots#botfather): The BotFather is the one bot to rule them all. Use it to create new bot accounts and manage your existing bots.
