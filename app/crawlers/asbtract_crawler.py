import abc
import datetime
from dataclasses import dataclass


@dataclass
class Offer:
    id: str
    title: str | None
    link: str
    price: int
    upload_string: str | None
    beginning: datetime.date | None
    until: datetime.date | None


class Crawler(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def crawl_offers(self) -> list[Offer]:
        raise NotImplementedError()

    @abc.abstractproperty
    def name(self) -> str:
        raise NotImplementedError()
