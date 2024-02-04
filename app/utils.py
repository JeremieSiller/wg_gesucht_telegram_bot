import re


def convert_price_to_int(price_string: str) -> int:
    result = re.sub("[^0-9]", "", price_string)
    try:
        return int(result)
    except ValueError:
        return 0
