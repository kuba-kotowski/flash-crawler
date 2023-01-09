import pandas as pd
import pymongo
import os
from dotenv import load_dotenv
from flash_crawler.flash_crawler import FlashCrawler

# load from .env file mongodb name ("MONGODB_NAME") & connection string ("MONGO_URI")
load_dotenv()
database_name = os.getenv("MONGODB_NAME")
mongodb_connection = pymongo.MongoClient(os.getenv("MONGO_URI"))[database_name]

spider = FlashCrawler(
	config_path="flashscore_config.yaml",
	headless_browser=False,
	mongodb=mongodb_connection
)

# scraping list of Serie A football games from next 7 days (overview) & saving to MongoDB collection 'next_week_serie_a_games':
future_games_overview = spider.get_future_games_list_overview(
	fixtures_url="https://www.flashscore.com/football/italy/serie-a/fixtures/",
	next_n_rounds=None,
	next_n_days=7,
	mongodb_collection_name="next_week_serie_a_games"
)
print([game.dict() for game in future_games_overview])

# scraping details of football UEFA Champions League game RB Leipzig vs Real Madrit (including detailed odds, events & stats)
# won't be saving the result to MongoDB (mongodb_collection_name=None):
detailed_game = spider.get_past_game_details(
	game_overview_url="https://www.flashscore.com/match/dlRWuADC/#/match-summary/match-summary", 
	odds=True, 
	events=True, 
	stats=True, 
	mongodb_collection_name=None # won't be saving this in MongoDB
)
print(detailed_game.dict())

# scraping details of football games in last round of Serie A (including detailed odds & stats, without events) & saving results to MongoDB collection 'past_serie_a_games':
past_games_details = spider.get_past_games_list_details(
	results_url="https://www.flashscore.com/football/italy/serie-a/results/",
	last_n_rounds=1,
	odds=True,
	events=False,
    stats=True,
	mongodb_collection_name="past_serie_a_games"
)
print([game.dict() for game in past_games_details])

spider.driver.browser.close()
spider.driver.playwright.stop()