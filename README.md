# FLASH-CRAWLER

Web-scraping project - extracting data from Flashscore.com

## Frameworks:
- web-scraping: [Playwright](https://playwright.dev/python/)
- data validation: [pydantic](https://pydantic-docs.helpmanual.io/)

## Instalation:
Install requirements from *requirements.txt* file:
```
pip install -r requirements.txt
```
Install playwright dependencies:
```
playwright install
```

## Usage:

### 1. FlashCrawler constructor:
``` python
spider = FlashCrawler(
    config_path="flashscore_config.yaml",
    headless_browser=False
    )
```
- `config_path: str` - path to yaml file with all css selectors needed to scrape webpage
- `headless_browser: bool` - use browser in headles or in windowed mode


### 2. FlashCrawler main methods:

#### FlashCrawler.get_past_game_details
Scrapes single past game's details (from detailed view - details, odds, events, stats).
``` python
past_game_details = spider.get_past_game_details(
    game_overview_url,
    odds=True, 
    events=True,
    stats=True
)
```
**Arguments**:
- `game_overview_url: str` - link to game's detailed view
[https://www.flashscore.com/match/K4ulGL9M/#/match-summary/match-summary]
- `odds: bool` - include detailed odds information, default True
- `events: bool` - include list of events (goals, cards, substitutions etc.), default True
- `stats: bool` - include stats, default True

**Returns `PastGameDetails` object:**
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
```python
class GameDetailedOdds(BaseModel):
    odds_dc_home: float                     # double chance 10 (home or draw)
    odds_dc_away: float                     # double chance 02 (away or draw)
    odds_over_15: float                     # over 1.5 goals
    odds_under_15: float                    # under 1.5 goals
    odds_over_25: float                     # over 2.5 goals
    odds_under_25: float                    # under 2.5 goals
```
``` python
class PastGameEvent(BaseModel):
    event_name: str                         # event name (goal, yellow_card, red_card, substitution etc.)
    time: int                               # minute of the game
    team: str                               # home/away - team which is connected with the event
    player: str                             # player which is connected with the event
```
``` python
class PastGameStat(BaseModel):
    stat_name: str                          # stat name (possesion, shots, corners etc.)
    home: Union[float, int]                 # home team's value
    away: Union[float, int]                 # away team's value
```

#### FlashCrawler.get_past_games_list_overview
Scrapes list of past games with overview (datetime, teams, goals).
``` python
past_game_details = spider.get_past_games_list_overview(
    results_url,
    last_n_rounds=1
)
```
**Arguments**:
- `results_url: str` - link to view with last games results (league or team specific view)
[https://www.flashscore.com/football/italy/serie-a/results/, https://www.flashscore.com/team/atalanta/8C9JjMXu/results/]
- `last_n_rounds: int` - number of last rounds (league view) or games (team view), default 1

**Returns list of `PastGameOverview` objects:**
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


#### FlashCrawler.get_past_games_list_details
Scrapes list of past games with detais (details, odds, events, stats).
``` python
past_game_details = spider.get_past_games_list_details(
    results_url,
    last_n_rounds=1,
    events=True,
    stats=True
)
```
**Arguments**:
- `results_url: str` - link to view with last games results (league or team specific view)
[https://www.flashscore.com/football/italy/serie-a/results/, https://www.flashscore.com/team/atalanta/8C9JjMXu/results/]
- `last_n_rounds: int` - number of last rounds (league view) or games (team view), default 1
- `odds: bool` - include detailed odds information, default True
- `events: bool` - include list of events (goals, cards, substitutions etc.), default True
- `stats: bool` - include stats, default True

**Returns list of [`PastGameDetails`](#### FlashCrawler.get_past_game_details) objects.**


## Authors:
- Jakub Kotowski

