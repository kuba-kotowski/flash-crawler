from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from fake_useragent import UserAgent
from time import sleep
from bs4 import BeautifulSoup
from typing import Dict, List


class ScrapingEngineError(Exception):
    pass

class ScrapingEngine:
    def __init__(
        self,
        headless=False,
        headers="",
        user_agent=UserAgent().chrome
        ) -> None:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.browser_context = self.browser.new_context(user_agent=user_agent)
        self.page = self.browser_context.new_page()
        stealth_sync(self.page)

    def navigate_to(self, url: str):
        self.page.goto(url, wait_until="load")
        self.parse_page_content()

    def parse_page_content(self):
        self.page_content = BeautifulSoup(self.page.content(), "html.parser")

    def get_popup_url(self, selector: str, container=None):
        # extraction of special element - url of the popup page showing up after click in the element (by selector) or in provided container
        with self.browser_context.expect_page() as new_page:
            if not container:
                self.page.locator(selector).click()
            else:
                container.click()
        new_page_value = new_page.value
        new_page_value.wait_for_load_state()
        popup_url = new_page_value.url
        new_page_value.close()
        return popup_url

    def find_one_by_selector(self, selector: str, attr=None, container=None):
        # find one element by selector within the page or in the provided container
        if not container:
            container = self.page
        if not selector and attr:
            return container.get_attribute(attr)
        elif attr=="text":
            return container.locator(selector).first.text_content(timeout=1000)
        elif attr:
            return container.locator(selector).first.get_attribute(attr, timeout=1000)
        else:
            return container.locator(selector).first

    def find_many_by_selector(self, selector: str, attr=None, container=None):
        # find many elements by selector within the page or in the provided container
        if not container:
            container = self.page
        containers = container.locator(selector)
        if not selector and attr:
            return [containers.nth(i).get_attribute(attr) for i in range(containers.count())]    
        elif attr:
            return [containers.nth(i).text_content() if attr=="text" else containers.nth(i).get_attribute(attr) for i in range(containers.count())]
        else:
            return [containers.nth(i) for i in range(containers.count())]

    @staticmethod
    def unpack_selector_string(selector_string: str):
        if selector_string.find("::") == -1:
            raise ScrapingEngineError("Incorrect selector string")
        selector, attr = selector_string.split("::")
        if selector and attr:
            return selector, attr
        elif not selector and attr:
            return None, attr
        elif selector and not attr:
            return selector, None
        else:
            return None, None

    def extract_one_element(self, key: str, one_element_selector: str, container=None) -> Dict:
        selector, attr = self.unpack_selector_string(one_element_selector)
        try:
            if not key.startswith("popup_url::"):
                return {key: self.find_one_by_selector(selector, attr, container)}
            else:
                return {key.split("::")[1]: self.get_popup_url(selector, container)}
        except Exception as e:
            # return {key: f"{e}"}
            return {key: ""}

    def extract_all_elements(self, all_elements_selectors: Dict, container=None) -> Dict:
        elements = dict()
        for key, selector_string in all_elements_selectors.items():
            elements.update(self.extract_one_element(key, selector_string, container))
        return elements

    def containers_extract_all_elements(self, containers: List, all_elements_selectors) -> List:
        elements = list()
        for container in containers:
            elements.append(self.extract_all_elements(all_elements_selectors, container))
        return elements

    def click(self, selector, **kwargs):
        self.page.click(selector, **kwargs)

    def css_exists(self, selector):
        locators = self.page.locator(selector)
        if locators.count() > 0:
            return True
        else: 
            return False