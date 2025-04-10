import re
import asyncio
from datetime import datetime

from settings import settings
import utils as utils

from src.v0.webdriver import Webdriver
from src.v0.base_pipelines import InfinityPaginationPipeline, overrides


# Adding special Scraper-based class for scraping games overview pages - popups with games details + pagination.
class PopupsScraper(InfinityPaginationPipeline):
    """
    Initial class for scraping games overview pages - popups with games details. Using Scraper as base class.
    Pagination added to limit or extend the number of games scraped.
    """
    url_suffix = None
    fields = {}
    containers_selector = None
    container_fields = {}
    click_selectors = []
    pagination_selector = ""

    def __init__(self, n_pagination=None, n_containers=None, last_n_days=None, popups_pool=4) -> None:
        """When using last_n_days, the datetime field must be defined in container_fields and field must by datetime type!"""
        super().__init__(n_pagination=n_pagination, n_containers=n_containers)
        if last_n_days and "datetime" not in self.container_fields.keys():
            raise ValueError("Last n days can be used only with datetime field")
        self.last_n_days = last_n_days
        self.popups_pool = popups_pool

    async def filter_containers(self, driver, containers):
        if self.n_containers:
            return containers[:self.n_containers]
        return containers
    
    async def handle_containers(self, driver, page):
        containers = await driver.locate_many_elements(page=page, selector=self.containers_selector)
        containers = await self.filter_containers(driver, containers)
        return containers

    async def handle_popup_by_idx(self, driver, page, context, idx):
        containers = await self.handle_containers(driver, page)
        popup_fields = await driver.handle_popup(
            page=containers[idx],
            popup_selector="",
            fields=self.container_fields,
            context=context
        )
        return popup_fields

    def get_if_gametime_within_last_n_days(self, popup_fields, last_n_days):
        if "process_datetime" in dir(self): # if process_datetime method is defined in the class
            gametime = self.process_datetime(popup_fields.get("datetime"))
        else:
            gametime = popup_fields.get("datetime")
        
        if type(gametime) != datetime:
            print("Cannot compare gametime with last_n_days, gametime is not datetime type")
        elif gametime and utils.get_days_diff(datetime.now(), gametime) >= last_n_days:
            return False
        return True

    async def handle_popups_in_context(self, driver, page, context, idxs):
        output = []
        for idx in idxs:
            popup_fields = await self.handle_popup_by_idx(driver, page, context, idx)
            if self.last_n_days:
                if not self.get_if_gametime_within_last_n_days(popup_fields, self.last_n_days):
                    break
            output.append(popup_fields)
        await context.close()
        return output

    async def handle_contexts(self, driver, url):
        contexts = []
        for i in range(self.popups_pool):
            page, context = await driver.new_page(new_context=True)
            contexts.append((page, context))
            await driver.navigate_to(page=page, url=url)
            await self.handle_default_driver_actions(driver=driver, page=page)
            await self.prepare_page(driver=driver, page=page)
        return contexts

    async def find_containers_number(self, driver, page):
        containers = await driver.locate_many_elements(page=page, selector=self.containers_selector)
        containers = await self.handle_containers(driver, page)
        return len(containers)

    @overrides(InfinityPaginationPipeline)
    async def scrape_fields(self, driver: Webdriver, page, **kwargs) -> dict:
        fields = await driver.get_all_fields(page=page, fields=self.fields)

        containers_number = await self.find_containers_number(driver, page)
        url = page.url
        contexts = await self.handle_contexts(driver, url)
        
        split = [(i, idx) for i in range(len(contexts)) for idx in range(i, containers_number, len(contexts))]
        tasks = [self.handle_popups_in_context(driver, contexts[i][0], contexts[i][1], [el[1] for el in split if el[0]==i]) for i in range(len(contexts))]
        output = await asyncio.gather(*tasks)
        output = [item for sublist in output for item in sublist]
        return [dict(**fields, **container_fields) for container_fields in output]

    @overrides(InfinityPaginationPipeline)
    def prepare_output(self, output):
        return output


class OverviewResultsOld(PopupsScraper):
    fields = {
        "season": ".container__livetable .heading__info::text"
    }
    containers_selector = ".event__match"
    container_fields = {
        "game_url": "{current_url}",
        "datetime": ".duelParticipant__startTime div::text",
        "league": ".tournamentHeader__country a::text",
        "home": ".duelParticipant__home a.participant__participantName::text",
        "home_url": ".duelParticipant__home a.participant__participantName::href",
        "away": ".duelParticipant__away a.participant__participantName::text",
        "away_url": ".duelParticipant__away a.participant__participantName::href",
    }
    click_selectors = [".langBoxSetup__button.langBoxSetup__button--stayBtn::optional", "button#onetrust-reject-all-handler::optional", ".close.wizard__closeIcon::optional"]
    pagination_selector = ".event__more.event__more--static"

    @staticmethod
    def process_season(value):
        match_season = re.search(r"\d{4}/\d{4}", value)
        if match_season:
            return match_season.group(0)
        else:
            return None

    @staticmethod
    def process_game_url(value):
        return utils.parse_base_url(value)

    @staticmethod
    def process_datetime(value):
        return  utils.parse_datetime(value, '%d.%m.%Y %H:%M')

    @staticmethod
    def process_league(value):
        return utils.parse_league(value)

    @staticmethod
    def process_home_url(value):
        return f"https://www.flashscore.com{value}"
    
    @staticmethod
    def process_away_url(value):
        return f"https://www.flashscore.com{value}"


class OverviewResults(InfinityPaginationPipeline):
    fields = {
        "season": ".container__livetable .heading__info::text"
    }
    containers_selector = ".event__match"
    container_fields = {
        "game_url": "a[href]::href",
        "datetime": ".event__time::text",
        "home": ".event__homeParticipant img::alt",
        "away": ".event__awayParticipant img::alt",
    }
    click_selectors = [".langBoxSetup__button.langBoxSetup__button--stayBtn::optional", "button#onetrust-reject-all-handler::optional", ".close.wizard__closeIcon::optional"]
    pagination_selector = ".event__more.event__more--static"

    @staticmethod
    def process_season(value):
        match_season = re.search(r"\d{4}/\d{4}", value)
        if match_season:
            return match_season.group(0)
        else:
            return None

    # @staticmethod
    # def process_game_url(value):
    #     return utils.parse_base_url(value)

    # @staticmethod
    # def process_datetime(value):
    #     return  utils.parse_datetime(value, '%d.%m.%Y %H:%M')

    # @staticmethod
    # def process_league(value):
    #     return utils.parse_league(value)

    # @staticmethod
    # def process_home_url(value):
    #     return f"https://www.flashscore.com{value}"
    
    # @staticmethod
    # def process_away_url(value):
    #     return f"https://www.flashscore.com{value}"


class OverviewH2H(PopupsScraper):
    url_suffix = "/#/h2h/overall"
    containers_selector = ".h2h__section.section:nth-child(${team}) .h2h__row"
    container_fields = {
        "game_url": "{current_url}",
        "datetime": ".duelParticipant__startTime div::text",
        "league": ".tournamentHeader__country a::text",
        "home": ".duelParticipant__home a.participant__participantName::text",
        "home_url": ".duelParticipant__home a.participant__participantName::href",
        "away": ".duelParticipant__away a.participant__participantName::text",
        "away_url": ".duelParticipant__away a.participant__participantName::href",
    }
    click_selectors = [".langBoxSetup__button.langBoxSetup__button--stayBtn::optional", "button#onetrust-reject-all-handler"]
    pagination_selector = ".h2h__section.section:nth-child(${team}) .showMore"

    def __init__(self, team: int = 1, *args, **kwargs):
        """team: 1 - home team games, 2 - away team games, 3 - h2h games"""
        self.team = team
        self.pagination_selector = self.pagination_selector.replace("${team}", str(self.team))
        self.containers_selector = self.containers_selector.replace("${team}", str(self.team))
        super().__init__(*args, **kwargs)

    @staticmethod
    def process_datetime(value):
        return  utils.parse_datetime(value, '%d.%m.%Y %H:%M')

    @staticmethod
    def process_league(value):
        return utils.parse_league(value)

    @staticmethod
    def process_home_url(value):
        return f"https://www.flashscore.com{value}"
    
    @staticmethod
    def process_away_url(value):
        return f"https://www.flashscore.com{value}"
