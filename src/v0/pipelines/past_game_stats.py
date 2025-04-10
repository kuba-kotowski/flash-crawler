import re

from settings import settings
import utils as utils

from src.v0.base_pipelines import BasePipeline, overrides


class PastGameStatistics(BasePipeline):
    url_suffix = "/#/match-summary/match-statistics/${section}"
    containers_selector = "div[data-testid='wcl-statistics']"
    container_fields = {
        "stat_name": "[data-testid='wcl-statistics-category']::text",
        "home": "[data-testid='wcl-statistics-value']:nth-child(1)::text",
        "away": "[data-testid='wcl-statistics-value']:nth-child(3)::text"
    }
    
    def __str__(self) -> str:
        return "past_game_stats"

    def __init__(self, section: int = 0) -> None:
        """Section means given half or full time stats. 0 is full time, 1 is first half, 2 is second half, 3 is extra time"""
        self.section = section
        super().__init__()

    async def run(self, driver = None, url: str = None, additional_output_data: dict = None, **kwargs):
        return {"stats": await super().run(self, driver=driver, url=url, additional_output_data=additional_output_data, **kwargs)}

    @overrides(BasePipeline)
    def prepare_url(self, url: str) -> str:
        url = super().prepare_url(url)
        return url.replace("${section}", str(self.section))

    @overrides(BasePipeline)
    async def prepare_page(self, driver, page):
        await driver.sleep(page=page, sec=3)

    @staticmethod
    def process_stat_name(value) -> str:
        if "Expected Goals (xG)" in value:
            return "expected_goals"
        else:
            return re.sub("[ |-]", "_", value.strip().lower())
    
    @staticmethod
    def parse_stat_value(value: str) -> int:
        if "%" not in value:
            try:
                return int(value)
            except ValueError:
                return float(value)
        else:
            return int(value.replace("%", ""))/100

    def process_home(self, value):
        return self.parse_stat_value(value)
    
    def process_away(self, value):
        return self.parse_stat_value(value)
