from time import sleep
from typing import Dict, List, Union

from .engines import ScrapingEngine, ConfigParser
from .utility_functions.parsing_functions import process_datetime, update_past_game_details, process_event, process_stat, update_future_game_details, filter_odds_over_under
from .models import PastGameOverview, PastGameDetails, FutureGameOverview, FutureGameDetails, PastGameEvent, PastGameStat, GameDetailedOdds


class FlashCrawler:
    def __init__(self, config_path: str, headless_browser: bool) -> None:
        self.driver = ScrapingEngine(headless=headless_browser)
        self.parser = ConfigParser(config_path=config_path)
        self.open_main_page()


    def __del__(self):
        self.driver.browser.close()
        self.driver.playwright.stop()


    def open_main_page(self):
        self.driver.navigate_to("https://www.flashscore.com")
        self.close_cookies()


    def close_cookies(self):
        sleep(1)
        try:
            self.driver.click("button#onetrust-accept-btn-handler", timeout=500)
            sleep(1)
        except:
            pass


    @staticmethod
    def check_url(url, type) -> str:
        validate = {
            "future": ["/fixtures", "/fixtures/"],
            "past": ["/results", "/results/"]
        }
        if url.endswith(tuple(validate.get(type))):
            pass
        else:
            raise Exception(f"Incorrect page url for {type} games list")


    @staticmethod
    def create_url_future_game_odds(base_url, odds_type) -> str:
        if odds_type == "double_chance":
            return base_url.replace("/match-summary", "/odds-comparison/double-chance/full-time")
        elif odds_type == "over_under":
            return base_url.replace("/match-summary", "/odds-comparison/over-under/full-time")


    @staticmethod
    def create_url_future_game_h2h(base_url) -> str:
        return base_url.replace("/match-summary", "/h2h/overall")


    @staticmethod
    def create_url_future_game_standings(base_url) -> str:
        return base_url.replace("/match-summary", "/standings/table/overall")


    @staticmethod
    def create_url_past_game_stats(base_url) -> str:
        if "match-summary/match-summary" in base_url:
            return base_url.replace("match-summary/match-summary", "match-summary/match-statistics/0")
        else:
            return base_url.replace("/match-summary", "match-summary/match-statistics/0")


    @staticmethod
    def filter_containers_rounds_view(containers, n_rounds):
        output_containers = []
        n = 1
        for container in containers:
            output_containers.append(container)
            if "--last" in container.get_attribute("class") and n == n_rounds:
                break
            elif "--last" in container.get_attribute("class"):
                n+=1
        return output_containers


    @staticmethod
    def filter_containers_games_view(containers, n_games):
        return containers[:n_games]


    def scrape_future_games(self, fixtures_url, next_n_rounds=1) -> List[FutureGameOverview]:
        """
        FUTURE GAMES OVERVIEW - LIST
        """
        self.check_url(fixtures_url, "future")
        self.driver.navigate_to(fixtures_url)
        if next_n_rounds > 10:
            next_n_rounds=10
        game_containers_selector = self.parser.get_containers_selector("overview/fixtures")
        game_containers_elements = self.parser.get_containers_elements_selectors("overview/fixtures")
        containers = self.driver.find_many_by_selector(selector=game_containers_selector)
        # get games only from n-next rounds:
        if fixtures_url.startswith("https://www.flashscore.com/team/"):
            selected_games = self.filter_containers_games_view(containers, next_n_rounds)
        else:
            selected_games = self.filter_containers_rounds_view(containers, next_n_rounds)

        elements = self.driver.containers_extract_all_elements(
            containers=selected_games, 
            all_elements_selectors=game_containers_elements
            )
        [element.update({
            "datetime": process_datetime(element.get("datetime"))
        }) for element in elements]
        
        return [FutureGameOverview(**element) for element in elements]

    
    @staticmethod
    def parse_past_games_argument(past_games) -> int:
        config = {
            "last_5": 0,
            "last_10": 1,
            "last_15": 2
        }
        if not past_games:
            return -1
        elif past_games not in config.keys():
            return -1
        else:
            return config[past_games]


    def scrape_future_game_details(
            self, 
            game_overview_url: str,
            odds=True, 
            past_games="last_5", past_games_details=True, past_games_events=True, past_games_stats=True, 
            current_standings=True
        ) -> FutureGameDetails:
        """
        FUTURE GAME - ALL DETAILS
        """
        self.driver.navigate_to(game_overview_url)
        game_overview_scenario = self.parser.get_elements_selectors("future_game/info")
        elements = self.driver.extract_all_elements(game_overview_scenario)
        elements = update_future_game_details(elements)
        elements["game_url"] = game_overview_url

        if odds:
            elements.update({
                "odds": self.scrape_game_odds(game_overview_url)
            })
        
        past_games_int = self.parse_past_games_argument(past_games)
        if past_games_int != -1 and not past_games_details:
            elements.update({
                "past_games_home": self.scrape_game_h2h(game_overview_url, "home", past_games_int),
                "past_games_away": self.scrape_game_h2h(game_overview_url, "away", past_games_int),
                "past_games_h2h": self.scrape_game_h2h(game_overview_url, "h2h", past_games_int)
            })
        elif past_games_int != -1 and past_games_details:
            elements.update({
                "past_games_home": self.scrape_game_h2h_details(game_overview_url, "home", past_games_int, past_games_events, past_games_stats),
                "past_games_away": self.scrape_game_h2h_details(game_overview_url, "away", past_games_int, past_games_events, past_games_stats),
                "past_games_h2h": self.scrape_game_h2h_details(game_overview_url, "h2h", past_games_int, past_games_events, past_games_stats)
            })
        
        if current_standings:
            # elements.update(self.scrape_standings)
            pass

        return FutureGameDetails(**elements)


    def scrape_future_games_details(
            self, 
            fixtures_url, next_n_rounds=1,
            odds=True, 
            past_games="last_5", past_games_details=True, past_games_events=True, past_games_stats=True, 
            current_standings=True
        ) -> List[FutureGameDetails]:
        games = self.scrape_future_games(fixtures_url, next_n_rounds)
        output = []
        for game in games:
            print(game.home)
            output.append(self.scrape_future_game_details(
                    game.game_url, 
                    odds, 
                    past_games, 
                    past_games_details, 
                    past_games_events, 
                    past_games_stats, 
                    current_standings
                ))
        return output


    def scrape_game_odds(self, game_overview_url: str) -> GameDetailedOdds:
        """
        FUTURE GAME ELEMENT - ODDS ALL
        """
        elements = self.scrape_game_odds_double_chance(game_overview_url)
        elements.update(self.scrape_game_odds_over_under(game_overview_url))
        return GameDetailedOdds(**elements)


    def scrape_game_odds_double_chance(self, game_overview_url: str) -> Dict:
        """
        FUTURE GAME ELEMENT - ODDS DOUBLE CHANCE
        """
        odds_url_double_chance = self.create_url_future_game_odds(base_url=game_overview_url, odds_type="double_chance")
        self.driver.navigate_to(odds_url_double_chance)
        double_chance_odds_scenario = self.parser.get_elements_selectors("future_game/odds/double-chance") 
        elements = self.driver.extract_all_elements(double_chance_odds_scenario)
        return elements


    def scrape_game_odds_over_under(self, game_overview_url: str) -> Dict:
        """
        FUTURE GAME ELEMENT - ODDS OVER/UNDER
        """
        odds_url_over_under = self.create_url_future_game_odds(base_url=game_overview_url, odds_type="over_under")
        self.driver.navigate_to(odds_url_over_under)
        over_under_odds_containers_selector = self.parser.get_containers_selector("future_game/odds/over-under")
        over_under_odds_elements_scenario = self.parser.get_containers_elements_selectors("future_game/odds/over-under")
        over_under_odds_containers = self.driver.find_many_by_selector(over_under_odds_containers_selector)
        odds_over_under = self.driver.containers_extract_all_elements(
            containers=over_under_odds_containers, 
            all_elements_selectors=over_under_odds_elements_scenario
            )
        # filter containers containing only first o/u 1.5 odds & first o/u 2.5 odds
        elements = filter_odds_over_under(odds_over_under)
        return elements


    def scrape_game_h2h(self, game_overview_url: str, h2h_type: str, show_more: int = 0) -> List[PastGameOverview]:
        """
        FUTURE GAME ELEMENT - H2H
        """
        h2h_url = self.create_url_future_game_h2h(game_overview_url)
        self.driver.navigate_to(h2h_url)
        sleep(1)
        i = 0
        while show_more != 0 and i < show_more:
            for n in [1, 2, 3]:
                self.driver.click(f".h2h__section.section:nth-child({n}) .h2h__showMore.showMore")
            i+=1
        h2h_type_config = {
            "home": "future_game/h2h/last_games_home",
            "away": "future_game/h2h/last_games_away",
            "h2h": "future_game/h2h/last_games_h2h"
        }
        game_containers_selector = self.parser.get_containers_selector(page_type=h2h_type_config[h2h_type])
        game_containers_elements = self.parser.get_containers_elements_selectors(page_type=h2h_type_config[h2h_type])
        game_containers = self.driver.find_many_by_selector(selector=game_containers_selector)
        elements = self.driver.containers_extract_all_elements(
            containers=game_containers,
            all_elements_selectors=game_containers_elements
        )
        [element.update({
            "datetime": process_datetime(element.get("datetime"))
        }) for element in elements]
        return [PastGameOverview(**element) for element in elements]


    def scrape_game_h2h_details(self, game_overview_url: str, h2h_type: str, show_more: int = 0, events: bool = True, stats: bool = False) -> List[PastGameDetails]:
        """
        FUTURE GAME ELEMENT - H2H DETAILS
        """
        past_games = self.scrape_game_h2h(game_overview_url, h2h_type, show_more)
        urls = [past_game.game_url for past_game in past_games]
        elements = [self.scrape_past_game_details(
            game_overview_url=url,
            events=events,
            stats=stats
        ) for url in urls]
        return elements


    def scrape_standings(self, game_overview_url: str, home: str, away: str) -> Dict: #TODO: which fields to include
        """
        FUTURE GAME ELEMENT - TABLE
        """
        table_url = self.create_url_future_game_standings(game_overview_url)
        self.driver.navigate_to(table_url)
        stand_continers_selector = self.parser.get_containers_selector(page_type="future_game/standings")
        stand_containers_elements = self.parser.get_containers_elements_selectors(page_type="future_game/standings")
        stand_containers = self.driver.find_many_by_selector(selector=stand_continers_selector)
        elements = self.driver.containers_extract_all_elements(
            containers=stand_containers,
            all_elements_selectors=stand_containers_elements
        )
        [element.update({"rank": int(element["rank"].replace(".", ""))}) for element in elements]
        points_leader = int([element["points"] for element in elements if element["rank"]==1][0])
        home_standing = [element for element in elements if element["team"]==home][0]
        away_standing = [element for element in elements if element["team"]==away][0]
        return {
            "rank_home": home_standing["rank"],
            "rank_away": away_standing["rank"],
            # "points_delta_leader_vs_home": points_leader-int(home_standing["points"]),
            # "points_delta_leader_vs_away": points_leader-int(away_standing["points"]),
            # "points_delta_home_vs_away": int(home_standing["points"])-int(away_standing["points"])
        }


    def scrape_past_games(self, results_url, last_n_rounds=1) -> List[PastGameOverview]:
        """
        PAST GAMES OVERVIEW - LIST
        """
        self.check_url(results_url, "past")
        self.driver.navigate_to(results_url)
        if last_n_rounds > 10:
            last_n_rounds=10
        game_containers_selector = self.parser.get_containers_selector("overview/results")
        game_containers_elements = self.parser.get_containers_elements_selectors("overview/results")
        containers = self.driver.find_many_by_selector(selector=game_containers_selector)
        # get games only from n-next rounds/games:
        if results_url.startswith("https://www.flashscore.com/team/"):
            selected_games = self.filter_containers_games_view(containers, last_n_rounds)
        else:
            selected_games = self.filter_containers_rounds_view(containers, last_n_rounds)

        elements = self.driver.containers_extract_all_elements(
            containers=selected_games, 
            all_elements_selectors=game_containers_elements
            )
        [element.update({
            "datetime": process_datetime(element.get("datetime"))
        }) for element in elements]

        return [PastGameOverview(**element) for element in elements]


    def scrape_past_game_details(self, game_overview_url: str, events=True, stats=True) -> PastGameDetails:
        """
        PAST GAME - ALL DETAILS
        """
        self.driver.navigate_to(game_overview_url)
        elements_scenario = self.parser.get_elements_selectors(page_type="past_game/info")
        elements = self.driver.extract_all_elements(
            all_elements_selectors=elements_scenario
        )
        if events:
            elements["events"] = self.scrape_past_game_events(game_overview_url)
        if stats:
            elements["stats"] = self.scrape_past_game_stats(game_overview_url)
        elements["game_url"] = game_overview_url
        return PastGameDetails(**update_past_game_details(elements))


    def scrape_past_game_events(self, game_overview_url: str) -> List[PastGameEvent]:
        """
        PAST GAME ELEMENT - EVENTS
        """
        self.driver.navigate_to(game_overview_url)
        sleep(1)
        event_containers_selector = self.parser.get_containers_selector(page_type="past_game/events")
        event_containers_elements = self.parser.get_containers_elements_selectors(page_type="past_game/events")
        event_containers = self.driver.find_many_by_selector(selector=event_containers_selector)
        elements = self.driver.containers_extract_all_elements(
            containers=event_containers,
            all_elements_selectors=event_containers_elements
        )
        return [PastGameEvent(**process_event(element)) for element in elements] 


    def scrape_past_game_stats(self, game_overview_url: str) -> List[PastGameStat]:
        """
        PAST GAME ELEMENT - STATISTICS
        """
        stats_url = self.create_url_past_game_stats(base_url=game_overview_url)
        self.driver.navigate_to(stats_url)
        sleep(1)
        stats_containers_selector = self.parser.get_containers_selector(page_type="past_game/stats")
        stats_containers_elements = self.parser.get_containers_elements_selectors(page_type="past_game/stats")
        stats_containers = self.driver.find_many_by_selector(selector=stats_containers_selector)
        elements = self.driver.containers_extract_all_elements(
            containers=stats_containers,
            all_elements_selectors=stats_containers_elements
        )
        return [PastGameStat(**process_stat(element)) for element in elements]


    def update_post_game_info(self, future_game: Union[FutureGameOverview, FutureGameDetails], events=True, stats=True) -> FutureGameOverview:
        """
        POST GAME - RESULTS & ADDITIONAL INFORMATION
        """
        elements = future_game.dict()
        past_game_details = self.scrape_past_game_details(
            game_overview_url=elements["game_url"],
            events=events, 
            stats=stats
            )
        elements.update(past_game_details.dict())
        return FutureGameDetails(**elements)
