# Kleinanzeigen + WG Gesucht Bot

This is a bot that scrapes new entries on Kleinanzeigen and/or WG Gesucht and sends notifications via Telegram when there is a new entry. It helps you stay updated on new listings for any search query you want.
I primarily used it to find new listings for apartments and shared flats and thats why wg-gesucht is also supported, but you can just use it as a Kleinazeigen bot if you want.

## Usage

To use this bot, follow these steps:

1. Clone the repository: `git clone https://github.com/JeremieSiller/kleinanzeigen_bot.git`
2. Install the dependencies using [Poetry](https://python-poetry.org/): `poetry install`
3. rename the `example.env` file to `.env`.
4. Obtain a Telegram Bot token from [BotFather](https://core.telegram.org/bots#botfather) and add it to the `.env` file under `TELEGRAM_TOKEN`.
5. Add the url you want to scrape to the `.env` file under `KLEINANZEIGEN_URL` and `WG_GESUCHT_URL` (e.g. `https://www.kleinanzeigen.de/s-berlin/anzeige:angebote/hertha-tickets/k0l3331`).
6. If you don't want to use WG Gesucht, set `WG_GESUCHT_URL` to `""`.
7. create file to keep chats persistent: `touch chats.ids` and set the IDS_FILE_NAME variable in the `.env` file to the name of the file you created (e.g. `chats.ids`)
8. Run the bot: `poetry run python main.py`
9. send `/start` to your bot and it will start scraping the urls you provided and send you a message with the new listings.

- if you want to use certain filters, just add them on kleinanzeigen/wg-gesucht and copy the new url to the `.env` file.

Alternatively, you can use Docker to run the bot:

1. Build the Docker image: `docker build -t telegram-scraper .`
2. Run the Docker container: `docker run telegram-scraper`

## License

This project is licensed under the [MIT License](LICENSE).

## Miscellaneous

This project was created as a learning experience and is not intended for production use. It is not affiliated with Kleinanzeigen or WG Gesucht.


## Additional Resources

- [Poetry](https://python-poetry.org/): A dependency management and packaging tool for Python.
- [BotFather](https://core.telegram.org/bots#botfather): The BotFather is the one bot to rule them all. Use it to create new bot accounts and manage your existing bots.
