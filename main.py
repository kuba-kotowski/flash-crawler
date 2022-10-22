from flash_crawler.flash_crawler import FlashCrawler

spider = FlashCrawler(
    config_path="flashscore_config.yaml",
    headless_browser=False
)

# scrape all info about games from next Bundesliga round:
games = spider.scrape_future_games_details(
    fixtures_url="https://www.flashscore.com/football/germany/bundesliga/fixtures/",
    next_n_rounds=1,
    odds=True,
    past_games="last_5",
    past_games_details=True, 
    past_games_events=False,
    past_games_stats=False,
    current_standings=False
)

spider.driver.browser.close()
spider.driver.playwright.stop()
