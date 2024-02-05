from urllib import parse

import bs4
import httpx

from app import utils

from . import asbtract_crawler


class KleinanzeigenCrawler(asbtract_crawler.Crawler):
    def __init__(self, url: str, filter_older_than_today: bool = True) -> None:
        self._url = url
        self._base_url = parse.urlparse(url).netloc
        self._filter_older_than_today = filter_older_than_today

    _headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    }

    def crawl_offers(self) -> list[asbtract_crawler.Offer]:
        with httpx.Client(http2=True) as client:
            result = client.get(self._url, headers=self._headers)
        soup = bs4.BeautifulSoup(result.text, "lxml")
        ads: list[bs4.Tag] = soup.find_all("article", {"class": "aditem"})
        dates: list[bs4.Tag] = soup.find_all(
            "div", {"class": "aditem-main--top--right"}
        )
        prices: list[bs4.Tag] = soup.find_all(
            "p", {"class": "aditem-main--middle--price-shipping--price"}
        )
        data_list = []
        for ad, date, price in zip(ads, dates, prices):
            if self._filter_older_than_today and date.text.find("Heute") == -1:
                continue
            sub_soup = bs4.BeautifulSoup(str(ad), "lxml")
            price = sub_soup.find(
                "p", {"class": "aditem-main--middle--price-shipping--price"}
            )
            price_as_int = utils.convert_price_to_int(price.text)
            data_list.append(
                asbtract_crawler.Offer(
                    id=ad["data-adid"],
                    link=self._base_url + ad["data-href"],
                    price=price_as_int,
                    title=None,
                    beginning=None,
                    until=None,
                    upload_string=date.text.strip(),
                )
            )
        return data_list

    @property
    def name(self) -> str:
        return "kleinanzeigen"
