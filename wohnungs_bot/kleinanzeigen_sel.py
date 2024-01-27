import random
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class KleinanzeigenCrawler:
    _accepted_cookies: bool

    def __init__(self, base_url: str, driver: webdriver.Chrome) -> None:
        self._base_url = base_url
        self._accepted_cookies = False
        self._driver = driver

    def load_base(self) -> None:
        self._driver.get(self._base_url)

    def accept_cookies(self) -> None:
        if self._accepted_cookies:
            return
        toast_xpath = "/html/body/div[2]/div/div/div/div"
        button_xpath = "/html/body/div[2]/div/div/div/div/div/div[3]/button[2]"
        element = WebDriverWait(self._driver, 15).until(
            EC.presence_of_element_located((By.XPATH, toast_xpath))
        )
        accept = element.find_element(By.XPATH, button_xpath)
        time.sleep(1.0)
        accept.click()
        self._accepted_cookies = True

    def get_all_ids_on_page(self) -> list[str]:
        list_items = self._driver.find_elements(By.CLASS_NAME, "ad-listitem")
        result: list[str] = []
        for item in list_items:
            try:
                id = item.find_element(By.TAG_NAME, "article").get_attribute(
                    "data-adid"
                )
                result.append(id)  # type: ignore
            except NoSuchElementException:
                continue
        return result

    def get_data_for_ids(self, ids: list[str]) -> list[dict[str, str | None]]:
        sub_url = "https://www.kleinanzeigen.de/s-anzeige/{id}"
        user_name_xpath = "/html/body/div[1]/div[2]/div/section[1]/section/aside/div[2]/div/div[1]/ul/li/span/span[1]/a"  # nofa
        company_name_xpath = "/html/body/div[1]/div[2]/div/section[1]/section/aside/div[2]/div[2]/div/ul/li/span/span[1]"  # nofa
        result = []
        for id in ids:
            print("sleeping")
            time.sleep(random.random() + 0.5)
            print("getting: ", sub_url.format(id=id))
            self._driver.get(sub_url.format(id=id))
            info = {
                "description": self._driver.find_element(
                    By.ID, "viewad-description-text"
                ).text,
                "location": self._driver.find_element(By.ID, "viewad-locality").text,
                "title": self._driver.find_element(By.ID, "viewad-title").text,
                "price": self._driver.find_element(By.ID, "viewad-price").text,
                "user_name": self._driver.find_element(By.XPATH, user_name_xpath)
                if self._driver.find_elements(By.XPATH, user_name_xpath)
                else None,
                "company": self._driver.find_element(By.XPATH, company_name_xpath)
                if not self._driver.find_elements(By.XPATH, user_name_xpath)
                else None,
                "url": sub_url.format(id=id),
            }
            result.append(info)
        return result  # type: ignore[return-value]

    @property
    def base_url(self) -> str:
        return self._base_url


# %%
