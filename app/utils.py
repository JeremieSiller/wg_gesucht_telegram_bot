def convert_price_to_int(price_string: str) -> int:
    stripped_string = price_string.strip()
    no_currency = stripped_string.replace("€", "").strip()

    no_seperator = no_currency.replace(".", "")
    try:
        return int(no_seperator)
    except ValueError:
        return 0
