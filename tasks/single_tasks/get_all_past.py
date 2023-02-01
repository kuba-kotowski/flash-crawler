import pandas as pd
from datetime import datetime, timedelta, date
from typing import List
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


def get_all_past_games(table_url, collection_name, past_n_days):
    # checking which games are already in db:
    db_games_urls = mongodb[collection_name].find({}, {"game_url": 1, "_id": 0})
    db_games_urls = list(set([game["game_url"].replace(
        "#/match-summary/match-summary", "#/match-summary") for game in db_games_urls]))

    # create FlashCrawler instance:
    spider = FlashCrawler(
        config_path="flashscore_config.yaml",
        headless_browser=True,
        mongodb=mongodb
    )

    # Get all teams that appeard in the provided tables (table_urls) - it might be tables from several seasons
    # teams_results = []
    # for table_url in table_urls:
    teams_results = spider.scrape_team_results_url_from_table(table_url)
    # teams_results = list(set(teams_results))

    games_overview = []
    for url in teams_results:
        games_overview += spider.get_past_games_list_overview(
			results_url=url, 
			past_n_days=past_n_days,
			show_more_max_n=7
		)
    games_urls = [game.dict().get("game_url") for game in games_overview]
    games_urls = [game_url.replace("#/match-summary/match-summary", "#/match-summary") for game_url in games_urls]
    games_urls = [game_url for game_url in list(set(games_urls)) if game_url not in db_games_urls]

    print(f"Teams' games: {len(games_urls)}")

    additional_h2h = []
    for url in games_urls:
        for h2h_type in ["home", "away", "h2h"]:
            additional_h2h += spider.scrape_game_h2h(
                game_overview_url=url,
                h2h_type=h2h_type,
                show_more=1
            )
    additional_h2h = [game.dict().get("game_url") for game in additional_h2h]
    additional_h2h = [game_url.replace("#/match-summary/match-summary", "#/match-summary") for game_url in additional_h2h]
    additional_h2h = [game_url for game_url in list(set(additional_h2h)) if game_url not in db_games_urls]

    games_list = list(set(games_urls + additional_h2h))

    print(f"Final list: {len(games_list)}")

    for url in games_list:
        spider.get_past_game_details(
            url,
            odds=True, 
            events=True,
            stats=True,
            mongodb_collection_name=collection_name
        )
        sleep(random())



if __name__ == "__main__":
    # table_urls = [
    #     "https://www.flashscore.com/football/italy/serie-a/standings/#/UcnjEEGS/table/overall"
    #     ]
    # collection_name = "football_main_italy"
    past_n_days = 1500
    
    collection_name = os.getenv["COLLECTION_NAME"]
    table_url = os.getenv["TABLE_URL"]

    get_all_past_games(
        table_url=table_url, # selected league
        collection_name=collection_name, # collection to drop results
        past_n_days=7 # last n-days, if None then it's based on the last date in DB
    )
