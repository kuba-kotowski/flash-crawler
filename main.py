import pandas as pd
import pymongo
import os

from dotenv import load_dotenv
load_dotenv()

from flash_crawler.flash_crawler import FlashCrawler


def past_games_details(results_url, last_n_rounds):
    spider = FlashCrawler(
        config_path="flashscore_config.yaml",
        headless_browser=False
    )
    output = spider.scrape_past_games_details(
        results_url=results_url,
        last_n_rounds=last_n_rounds
    )
    spider.driver.browser.close()
    spider.driver.playwright.stop()

    return output



if __name__ == "__main__":
    results_url = "https://www.flashscore.com/football/europe/champions-league/results/"
    last_n_rounds = 30
    output = past_games_details(
        url=results_url, 
        last_n_rounds=last_n_rounds
        )
    print(output)