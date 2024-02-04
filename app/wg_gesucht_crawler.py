from urllib import parse

import bs4
import httpx

from app import utils
from app.crawlers import asbtract_crawler


class WgGesuchtCrawler(asbtract_crawler.Crawler):
    def __init__(self, url: str) -> None:
        self._url = url
        self._base_url = parse.urlparse(url).netloc

    def crawl_offers(self) -> list[asbtract_crawler.Offer]:
        result = httpx.get(self._url)
        soup = bs4.BeautifulSoup(result.text)
        offers = soup.find_all("div", {"class": "offer_list_item"})

        wg_offers = []
        for offer in offers:
            sub_soup = bs4.BeautifulSoup(str(offer), "lxml")
            h3_title = sub_soup.find("h3", {"class", "truncate_title"})
            a_href = sub_soup.find("a")
            b_price = sub_soup.find("b")
            id = sub_soup.find("div").attrs["data-id"]
            wg_offers.append(
                asbtract_crawler.Offer(
                    id=id,
                    title=h3_title.attrs["title"],
                    link=self._base_url + a_href.attrs["href"],
                    price=utils.convert_price_to_int(b_price.string),
                )
            )

        return wg_offers

    @property
    def name(self) -> str:
        return "wg_gesucht"
