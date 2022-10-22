
## FLASH-CRAWLER

Web-scraping project - extracting data from Flashscore.com

### packages used

- web-scraping: [Playwright](https://playwright.dev/python/). 
- data validation: [pydantic](https://pydantic-docs.helpmanual.io/). 

### FlashCrawler
**Define the class**:
``` python
spider = FlashCrawler(
    config_path="flashscore_config.yaml",
    headless_browser=False
    )
```
- `config_path` - path to yaml file with all css selectors needed to scrape webpage
- `headless_browser` - wheter to use browser in headles or in windowed mode


**Scrape list of future games for the given league or team** 
```python
spider.scrape_future_games(
    fixtures_url="https://www.flashscore.com/football/germany/bundesliga/fixtures/", 
    next_n_rounds=1
    )
```
- `fixtures_url` - url to the page with future games for given league or team. 
league view: https://www.flashscore.com/football/germany/bundesliga/fixtures/  
team view: https://www.flashscore.com/team/liverpool/lId4TMwf/fixtures/
- `next_n_rounds` - number of nearest round (league view) or games (team view) to be scraped



