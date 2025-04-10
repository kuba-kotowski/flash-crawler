import asyncio

from settings import settings
import utils as utils

from src.v0.base_pipelines import BasePipeline, overrides


class GameOddsResult(BasePipeline):
    url_suffix = "/#/odds-comparison/1x2-odds/full-time"
    fields = {
        "odds_home": ".ui-table__body .ui-table__row:nth-child(1) .oddsCell__odd:nth-child(2) span::text",
        "odds_draw": ".ui-table__body .ui-table__row:nth-child(1) .oddsCell__odd:nth-child(3) span::text",
        "odds_away": ".ui-table__body .ui-table__row:nth-child(1) .oddsCell__odd:nth-child(4) span::text"
    }

    @overrides(BasePipeline)
    async def prepare_page(self, driver, page, **kwargs):
        """Struggling with missing values - need to wait for the selector to appear on the page."""
        for selector in self.fields.values():
            await driver.wait_for_selector(page=page, selector=selector.split("::")[0])

    @staticmethod
    def process_odds_home(value):
        return utils.parse_float(value)
    
    @staticmethod
    def process_odds_draw(value):
        return utils.parse_float(value)
    
    @staticmethod
    def process_odds_away(value):
        return utils.parse_float(value)


class GameOddsDoubleChance(BasePipeline):
    url_suffix = "/#/odds-comparison/double-chance/full-time"
    fields = {
        "odds_dc_home": ".ui-table__body .ui-table__row:nth-child(1) .oddsCell__odd:nth-child(2) span::text",
        "odds_dc_away":  ".ui-table__body .ui-table__row:nth-child(1) .oddsCell__odd:nth-child(4) span::text"
    }

    @overrides(BasePipeline)
    async def prepare_page(self, driver, page, **kwargs):
        """Struggling with missing values - need to wait for the selector to appear on the page."""
        for selector in self.fields.values():
            await driver.wait_for_selector(page=page, selector=selector.split("::")[0])

    @staticmethod
    def process_odds_dc_home(value):
        return utils.parse_float(value)
    
    @staticmethod
    def process_odds_dc_away(value):
        return utils.parse_float(value)


class GameOddsBtts(BasePipeline):
    url_suffix = "/#/odds-comparison/both-teams-to-score/full-time"
    fields = {
        "odds_btts_yes": ".ui-table__body .ui-table__row:nth-child(1) .oddsCell__odd:nth-child(2) span::text",
        "odds_btts_no": ".ui-table__body .ui-table__row:nth-child(1) .oddsCell__odd:nth-child(3) span::text"
    }

    @overrides(BasePipeline)
    async def prepare_page(self, driver, page, **kwargs):
        """Struggling with missing values - need to wait for the selector to appear on the page."""
        for selector in self.fields.values():
            await driver.wait_for_selector(page=page, selector=selector.split("::")[0])

    @staticmethod
    def process_odds_btts_yes(value):
        return utils.parse_float(value)
    
    @staticmethod
    def process_odds_btts_no(value):
        return utils.parse_float(value)


class GameOddsOverUnder(BasePipeline):
    url_suffix = "/#/odds-comparison/over-under/full-time"
    containers_selector = ".ui-table.oddsCell__odds:nth-child(2n-1) .ui-table__row:nth-child(1)"
    container_fields = {
        "goals": ".oddsCell__noOddsCell::text",
        "odds_over": ".oddsCell__odd:nth-child(3)::text",
        "odds_under": ".oddsCell__odd:nth-child(4)::text"
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.output_type = dict

    @overrides(BasePipeline)
    async def prepare_page(self, driver, page, **kwargs):
        await driver.sleep(page=page, sec=3)

    @staticmethod
    def process_goals(value):
        return utils.parse_float(value)
    
    @staticmethod
    def process_odds_over(value):
        return utils.parse_float(value)
    
    @staticmethod
    def process_odds_under(value):
        return utils.parse_float(value)

    @overrides(BasePipeline)
    def prepare_output(self, output):
        final_output = dict()
        [final_output.update({
            f"odds_over_{field['goals']}": field["odds_over"],
            f"odds_under_{field['goals']}": field["odds_under"]
        }) for field in output]
        return final_output


class DetailedOdds:
    def __init__(self) -> None:
        self.output_type = list
        
    def __str__(self) -> str:
        return "detailed_odds"

    async def run(self, driver=None, url=None, *args, **kwargs):
        output = await asyncio.gather(*[
            GameOddsResult().run(driver, url, *args, **kwargs),
            GameOddsDoubleChance().run(driver, url, *args, **kwargs),
            GameOddsBtts().run(driver, url, *args, **kwargs),
            GameOddsOverUnder().run(driver, url, *args, **kwargs)
        ])
        output = {k: v for sublist in output for k, v in sublist.items()}
        return output