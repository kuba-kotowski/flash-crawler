import pandas as pd
from datetime import datetime, timedelta, date
import pymongo
import os
import sys
from random import random
from time import sleep
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from flash_crawler.flash_crawler import FlashCrawler

# load env variables mongodb name ("MONGODB_NAME") & connection string ("MONGO_URI")
load_dotenv()
database_name = os.getenv("MONGODB_NAME")
mongodb = pymongo.MongoClient(os.getenv("MONGO_URI"))[database_name]


def get_teams_latest(table_url: str, collection_name: str, past_n_days=7):
    """
    Scraping details for last games of teams from the given league (based on the table standings).
    Either based on the last date in DB or from last n-days but not games that already in DB.
    """
    # checking which games are already in db:
    db_games_urls = mongodb[collection_name].find({}, {"game_url": 1, "_id": 0})
    db_games_urls = list(set([game["game_url"].replace(
        "#/match-summary/match-summary", "#/match-summary") for game in db_games_urls]))

    # taking games since last date (included) in the mongodb:
    if not past_n_days:
        sort_dates = mongodb[collection_name].find(
            {}, {"datetime": 1, "_id": 0}).sort("datetime", -1).limit(1)
        if sort_dates:
            max_date = sort_dates[0]["datetime"].date()
            delta = date.today() - max_date
            delta_days = delta.days - 1  # not to include the day of the last game
        else: 
            raise Exception(f"Cannot caluclate delta days based on data from {collection_name}")

    if past_n_days:
        delta_days = past_n_days

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
            past_n_days=delta_days,
            show_more_max_n=1
        )
    games_urls = [game.dict().get("game_url") for game in games_overview]
    games_urls = [link.replace(
        "#/match-summary/match-summary", "#/match-summary") for link in games_urls]
    games_urls = list(set(games_urls))
    print(len(games_urls))
    games_urls = [game_url for game_url in games_urls if game_url not in db_games_urls]
    print(len(games_urls))

    for url in games_urls:
        spider.get_past_game_details(
            url,
            odds=True,
            events=True,
            stats=True,
            mongodb_collection_name=collection_name
        )
        sleep(random())
    
    spider.driver.browser.close()
    spider.driver.playwright.stop()



if __name__ == "__main__":
    table_url = "https://www.flashscore.com/football/italy/serie-a/standings/#/UcnjEEGS/table/overall"
    collection_name = "football_main_v2"
    past_n_days = 7

    get_teams_latest(
        table_url=table_url, # selected league
        collection_name=collection_name, # collection to drop results
        past_n_days=7 # last n-days, if None then it's based on the last date in DB
    )
