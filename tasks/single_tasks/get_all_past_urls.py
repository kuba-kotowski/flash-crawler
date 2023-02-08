import pymongo
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from flash_crawler.flash_crawler import FlashCrawler

# load env variables mongodb name ("MONGODB_NAME") & connection string ("MONGO_URI")
load_dotenv()
database_name = os.getenv("MONGODB_NAME")
mongodb = pymongo.MongoClient(os.getenv("MONGO_URI"))[database_name]


def get_teams_latest(table_url: str, collection_name: str, past_n_days=360):
    """
    Scraping details for last games of teams from the given league (based on the table standings).
    Either based on the last date in DB or from last n-days but not games that already in DB.
    """
    # create FlashCrawler instance:
    spider = FlashCrawler(
        config_path="flashscore_config.yaml",
        headless_browser=True,
        mongodb=mongodb
    )

    teams_results = spider.scrape_team_results_url_from_table(table_url)

    games_overview = []
    for url in teams_results:
        games_overview += spider.get_past_games_list_overview(
            results_url=url,
            past_n_days=past_n_days,
            show_more_max_n=10,
            mongodb_collection_name=collection_name
        )
    games_urls = [game.dict().get("game_url") for game in games_overview]
    games_urls = [link.replace(
        "#/match-summary/match-summary", "#/match-summary") for link in games_urls]
    games_urls = list(set(games_urls))

    additional_h2h = []
    for url in games_urls:
        for h2h_type in ["home", "away", "h2h"]:
            try:
                additional_urls = spider.scrape_game_h2h(
                    game_overview_url=url,
                    h2h_type=h2h_type,
                    show_more=3
                )
                additional_urls = [url for url in additional_urls if url.dict().get("game_url") not in games_urls]
                mongodb[collection_name].insert_many(additional_urls)
                additional_h2h+=additional_urls
            except Exception as e:
                mongodb["missing_h2h_urls"].insert_one({"url": url, "exception": str(e)})
    
    spider.driver.browser.close()
    spider.driver.playwright.stop()


if __name__ == "__main__":
    # table_url = "https://www.flashscore.com/football/italy/serie-a/standings/#/UcnjEEGS/table/overall"
    # collection_name = "football_main_v2"
    # past_n_days = 3
    
    table_url = os.getenv("TABLE_URL")
    collection_name = os.getenv("COLLECTION_NAME")
    past_n_days = os.getenv("PAST_N_DAYS")

    get_teams_latest(
        table_url=table_url, # selected league
        collection_name=collection_name, # collection to drop results
        past_n_days=int(past_n_days) # last n-days, if None then it's based on the last date in DB
    )
