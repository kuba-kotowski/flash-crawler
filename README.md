# Flash-crawler
Web-scraping project which aim is to scrape, process and save the data from [**Flashscore**](Flashscore.com). 

## Table of Contents:
1. [Prerequisites](#prerequisites)
2. [Getting started](#gettingstarted)
3. [Quick start](#quickstart)
4. [Usage](#usage)
	- [FlashCrawler.get_future_game_details](#flascrawlerget_future_game_details)
	- [FlashCrawler.get_future_games_list_overview](#flascrawlerget_future_games_list_overview)
	- [FlashCrawler.get_future_games_list_details](#flascrawlerget_future_games_list_details)
	- [FlashCrawler.get_past_game_details](#flascrawlerget_past_game_details)
	- [FlashCrawler.get_past_games_list_overview](#flascrawlerget_past_games_list_overview)
	- [FlashCrawler.get_past_games_list_details](#flascrawlerget_past_games_list_details)
	- [FlashCrawler.update_post_game_info]()
5. [Models](#models)
	- [FutureGameDetails](#futuregamedetails)
	- [FutureGameOverview](futuregameoverview)
	- [PastGameDetails](pastgamedetails)
	- [PastGameOverview](pastgameoverview)
	- [GameDetailedOdds](gamedetailedodds)
	- [PastGameStat](pastgamestat)
	- [PastGameEvent](pastgameevent)
6. [Config file](#configfile)
7. [Built With](#builtwith)
8. [Author](#author)

# Prerequisites
Install **requirements** from *requirements.txt* file:
```
pip install -r requirements.txt
```
Install **playwright binaries**:
```
playwright install
```
# Getting started
Create **FlashCrawler instance**:
``` python
spider = FlashCrawler(
    config_path="flashscore_config.yaml",
    headless_browser=False,
    mongodb=None
)
```
- `config_path: str` - path to yaml file with all css selectors needed to scrape webpage
- `headless_browser: bool` - use browser in headles or in windowed mode
- `mongodb: pymongo.MongoClient.db` - connection with selected MongoDB

# Quick start
```python
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv

# load from .env file mongodb name ("MONGODB_NAME") & connection string ("MONGO_URI")
load_dotenv()
database_name = os.getenv("MONGODB_NAME")
mongodb_connection = pymongo.MongoClient(os.getenv("MONGO_URI"))[database_name]

spider = FlashCrawler(
	config_path="flashscore_config.yaml",
	headless_browser=False,
	mongodb=mongodb_connection
)
```
- scraping list of Serie A football games from next 7 days (overview) & saving to MongoDB collection *next_week_serie_a_games*:
```python
future_games_overview = spider.get_future_games_list_details(
	fixtures_url="https://www.flashscore.com/football/italy/serie-a/fixtures/",
	next_n_rounds=None,
	next_n_days=7,
	mongodb_collection_name="next_week_serie_a_games"
)
print([game.dict() for game in future_games_overview])
```
- scraping details of football UEFA Champions League game RB Leipzig vs Real Madrit (including detailed odds, events & stats) - won't be saving the result to MongoDB (mongodb_collection_name=None):
```python
detailed_game = spider.get_past_game_details(
	game_overview_url="https://www.flashscore.com/match/dlRWuADC/#/match-summary/match-summary", 
	odds=True, 
	events=True, 
	stats=True, 
	mongodb_collection_name=None # won't be saving this in MongoDB
)
print(detailed_game.dict())
```
- scraping details of football games in last round of Serie A (including detailed odds & stats, without events) & saving results to MongoDB collection *past_serie_a_games*:
```python
past_games_details = spider.get_past_games_list_details(
	results_url="https://www.flashscore.com/football/italy/serie-a/results/",
	last_n_rounds=1,
	odds=True,
	events=False,
    stats=True,
	mongodb_collection_name="past_serie_a_games"
)
print([game.dict() for game in past_games_details])
```

Once you finished scraping close browser and stop playwright:
```python
spider.driver.browser.close()
spider.driver.playwright.stop()
```

# Usage
Find detailed description of main FlashCrawler's methods:
- [`FlashCrawler.get_future_game_details`](#flascrawlerget_future_game_details) - single future game's details
- [`FlashCrawler.get_future_games_list_overview`](#flascrawlerget_future_games_list_overview) - list of future games' overview
- [`FlashCrawler.get_future_games_list_details`](#flascrawlerget_future_games_list_details) - list of future games' details
- [`FlashCrawler.get_past_game_details`](#flascrawlerget_past_game_details) - single past game's details
- [`FlashCrawler.get_past_games_list_overview`](#flascrawlerget_past_games_list_overview) - list of past games' overview
- [`FlashCrawler.get_past_games_list_details`](#flascrawlerget_past_games_list_details) - list of past games' details
- [`FlashCrawler.update_post_game_info`]() - post-game update of previously scraped future game

## FlashCrawler.get_future_game_details
Scrapes single future game's details (from detailed view - details, odds, standings, h2h games with events/stats).
``` python
future_game_details = spider.get_future_game_details(
	game_overview_url,
	odds=True,
	past_games="last_5",
	past_games_details=True,
	past_games_events=True,
	past_games_stats=True,
	current_standings=True,
	mongodb_collection_name=None
)
```
**Arguments**:
- `game_overview_url: str` - link to future game's detailed view
example: https://www.flashscore.com/match/hviCPdIh/#/match-summary
- `odds: bool` - include detailed odds information, default True
- `past_games: str` - number of , default "last_5"
- `past_games_details: bool` - include details for past games (h2h), default True
- `past_games_events: bool` - include list of events (goals, cards, substitutions etc.) for past games (h2h), default True
- `past_games_stats: bool`- include stats for past games (h2h), default True
- `current_standings: bool`- include info from current table (positions, points diff), default True
- `mongodb_collection_name: str`- name of MongoDB collection name (doesn't save if eqauls to None), default None

**Returns**:
 - `FutureGameDetails` object


## FlashCrawler.get_future_games_list_overview
Scrapes list of future games with overview (datetime, teams).
``` python
future_game_details = spider.get_future_games_list_overview(
	fixtures_url, 
	next_n_rounds=1, 
	next_n_days=None,
	mongodb_collection_name=None
)
```
**Arguments**:
- `fixtures_url: str` - link to game's detailed view
example: https://www.flashscore.com/football/italy/serie-a/fixtures/, https://www.flashscore.com/team/as-roma/zVqqL0ma/fixtures/
- `next_n_rounds: int` - number of next rounds (league view) or games (team view), default 1
- `next_n_days: int` - games only from next n-days (overwrite the next_n_rounds argument), default None
- `mongodb_collection_name` - name of MongoDB collection name (doesn't save if eqauls to None), default None

**Returns**:
 - list of `FutureGameOverview` objects


## FlashCrawler.get_future_games_list_details
Scrapes list of future games with details (from detailed view - details, odds, standings, h2h games with events/stats).
``` python
future_game_details = spider.get_future_games_list_details(
	fixtures_url,
	next_n_rounds=1,
	next_n_days=None,
	odds=True,
	past_games="last_5",
	past_games_details=True,
	past_games_events=True,
	past_games_stats=True,
	current_standings=True,
	mongodb_collection_name=None
)
```
**Arguments**:
- `fixtures_url: str` - link to fixtures view (list of future games) - league view or team view
example: https://www.flashscore.com/football/italy/serie-a/fixtures/, https://www.flashscore.com/team/as-roma/zVqqL0ma/fixtures/
- `next_n_rounds: int` - number of next rounds (league view) or games (team view), default 1
- `next_n_days: int` - games only from next n-days (overwrite the next_n_rounds argument), default None
- `odds: bool` - include detailed odds information, default True
- `past_games: str` - number of h2h games (last_5 | last_10 | last_15), if None then doesn't scrape h2h section, default "last_5"
- `past_games_details: bool` - include details for past games (h2h section), default True (if past_games=None then past_games_details is overwritten with False)
- `past_games_odds: bool` - include detailed odds for past games (h2h), default True (missed if past_games_details=False)
- `past_games_events: bool` - include list of events (goals, cards, substitutions etc.) for past games (h2h), default True (missed if past_games_details=False)
- `past_games_stats: bool`- include stats for past games (h2h), default True (missed if past_games_details=False)
- `current_standings: bool`- include info from current table (positions, points diff), default True
- `mongodb_collection_name: str`- name of MongoDB collection name (doesn't save if eqauls to None), default None

**Returns**:
 - list of `FutureGameDetails` objects
 
 
## FlashCrawler.get_past_game_details
Scrapes single past game's details (from detailed view - details, odds, events, stats).
``` python
past_game_details = spider.get_past_game_details(
    game_overview_url,
    odds=True, 
    events=True,
    stats=True,
    mongodb_collection_name=None
)
```
**Arguments**:
- `game_overview_url: str` - link to game's detailed view
example: https://www.flashscore.com/match/K4ulGL9M/#/match-summary/match-summary
- `odds: bool` - include detailed odds information, default True
- `events: bool` - include list of events (goals, cards, substitutions etc.), default True
- `stats: bool` - include stats, default True
- `mongodb_collection_name: str`- name of MongoDB collection name (doesn't save if eqauls to None), default None

**Returns**:
 - `PastGameDetails` object

## FlashCrawler.get_past_games_list_overview
Scrapes list of past games with overview (datetime, teams, goals).
``` python
past_game_details = spider.get_past_games_list_overview(
    results_url,
    last_n_rounds=1,
    mongodb_collection_name=None
)
```
**Arguments**:
- `results_url: str` - link to view with last games results (league or team specific view)
example: https://www.flashscore.com/football/italy/serie-a/results/, https://www.flashscore.com/team/atalanta/8C9JjMXu/results/
- `last_n_rounds: int` - number of last rounds (league view) or games (team view), default 1
- `mongodb_collection_name: str`- name of MongoDB collection name (doesn't save if eqauls to None), default None

**Returns:**
- list of `PastGameOverview` objects


## FlashCrawler.get_past_games_list_details
Scrapes list of past games with details (details, odds, events, stats).
``` python
past_game_details = spider.get_past_games_list_details(
    results_url,
    last_n_rounds=1,
    odds=True,
    events=True,
    stats=True,
    mongodb_collection_name=None
)
```
**Arguments**:
- `results_url: str` - link to view with last games results (league or team specific view)
example: https://www.flashscore.com/football/italy/serie-a/results/, https://www.flashscore.com/team/atalanta/8C9JjMXu/results/
- `last_n_rounds: int` - number of last rounds (league view) or games (team view), default 1
- `odds: bool` - include detailed odds information, default True
- `events: bool` - include list of events (goals, cards, substitutions etc.), default True
- `stats: bool` - include stats, default True
- `mongodb_collection_name: str`- name of MongoDB collection name (doesn't save if eqauls to None), default None

**Returns:**
- list of [`PastGameDetails`](#flashcrawlerget_past_game_details) objects



# Models

Find details of used models:
- [FutureGameDetails](#futuregamedetails) - future game's details
- [FutureGameOverview](#futuregameoverview) - future game's overview
- [PastGameDetails](#pastgamedetails) - past game's details
- [PastGameOverview](#pastgameoverview) - past game's overview
- [GameDetailedOdds](gamedetailedodds) - details odds for future/past game
- [PastGameStat](#pastgamestat) - single statistic for past game (possesions, shots, offsides, corners etc.)
- [PastGameEvent](#pastgameevent) - single event for past game (goal, substitution, yellow/red card etc.)


# Models
List of all models.

## FutureGameDetails

```python
class FutureGameDetails(BaseModel):
	game_url: str																# link to game's detailed view
	league: str                                                                 # league
	round: str                                                                  # round
	datetime: datetime.datetime                                                 # datetime of game's start
	home: str                                                                   # home team's name
	away: str                                                                   # away team's name
	  
	referee: str                                                                # main referee

	odds_home: float                                                            # odds for home team's win
	odds_away: float                                                            # odds for away team's win
	odds_draw: float                                                            # odds for draw
	odds: Optional[GameDetailedOdds]                                            # detailed odds

	past_games_home: Optional[List[Union[PastGameDetails, PastGameOverview]]]   # list of home team's past games' overview/details 
	past_games_away: Optional[List[Union[PastGameDetails, PastGameOverview]]]   # list of away team's past games' overview/details 
	past_games_h2h: Optional[List[Union[PastGameDetails, PastGameOverview]]]    # list of head-to-head past games' overview/details

	# post-game details:
	goals_home: Optional[int]                                                   # goals scored by home team
	goals_away: Optional[int]                                                   # goals scored by away team
	events: Optional[List[PastGameEvent]]                                       # list of events (goals, cards, substitutions etc.)
	stats: Optional[List[PastGameStat]] #                                       # list of stats (possesion, shots, corners, offsides etc.)
	odds_winner: Optional[float]                                                # odds for game's final result
	attendance: Optional[int]                                                   # attendance
```
See models:  [`PastGameDetails`](#pastgamedetails), [`PastGameOverview`](#pastgameoverview), [`GameDetailedOdds`](#gamedetailedodds), [`PastGameEvent`](#pastgameevent), [`PastGameStat`](#pastgamestat)

## FutureGameOverview

```python
class FutureGameOverview(BaseModel):
    datetime: datetime.datetime             # datetime of game's start 
    game_url: str                           # link to game's detailed view
    home: str                               # home team's name
    away: str                               # away team's name
```

## PastGameDetails

```python
class PastGameDetails(BaseModel):
    game_url: str                           # link to game's detailed view
    league: str                             # league
    round: str                              # round
    datetime: datetime.datetime             # datetime of game's start
    home: str                               # home team's name
    away: str                               # away team's name
    goals_home: int                         # goals scored by home team
    goals_away: int                         # goals scored by away team
    odds_home: float                        # odds for home team's win
    odds_draw: float                        # odds for draw
    odds_away: float                        # odds for away team's win
    odds: Optional[GameDetailedOdds]        # detailed odds
    events: Optional[List[PastGameEvent]]   # list of events (goals, cards, substitutions etc.)
    stats: Optional[List[PastGameStat]]     # list of stats (possesion, shots, corners, offsides etc.)
    referee: str                            # main referee
    attendance: int                         # attendance
```
See models:  [`GameDetailedOdds`](#gamedetailedodds), [`PastGameEvent`](#pastgameevent), [`PastGameStat`](#pastgamestat)

## PastGameOverview

```python
class PastGameOverview(BaseModel):
    datetime: datetime.datetime             # datetime of game's start
    league: Optional[str]                   # league
    round: Optional[str]                    # round
    game_url: str                           # link to game's detailed view
    home: str                               # home team's name
    away: str                               # away team's name
    goals_home: int                         # goals scored by home team
    goals_away: int                         # goals scored by away team
```

## GameDetailedOdds

```python
class GameDetailedOdds(BaseModel):
    odds_dc_home: float                     # double chance 10 (home or draw)
    odds_dc_away: float                     # double chance 02 (away or draw)
    odds_over_15: float                     # over 1.5 goals
    odds_under_15: float                    # under 1.5 goals
    odds_over_25: float                     # over 2.5 goals
    odds_under_25: float                    # under 2.5 goals
```

## PastGameEvent

``` python
class PastGameEvent(BaseModel):
    event_name: str                         # event name (goal, yellow_card, red_card, substitution etc.)
    time: int                               # minute of the game
    team: str                               # home/away - team which is connected with the event
    player: str                             # player which is connected with the event
```

## PastGameStat

``` python
class PastGameStat(BaseModel):
    stat_name: str                          # stat name (possesion, shots, corners etc.)
    home: Union[float, int]                 # home team's value
    away: Union[float, int]                 # away team's value
```

# Config file
to be added - description of yaml config file containing css selectors

# Built With
- [Playwright](https://playwright.dev/python/) 					| web-scraping
- [pydantic](https://pydantic-docs.helpmanual.io/) 				| data validation
- [pyMongo](https://pymongo.readthedocs.io/en/stable/) 	        | working with MongoDD
- [PyYAML](https://pyyaml.org/) 							    | working with YAML files


# Author 
Jakub Kotowski :wave: