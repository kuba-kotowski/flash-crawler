from pydantic import BaseModel, validator
import datetime

from typing import List, Optional, Union


class PastGameStat(BaseModel):
    stat_name: str
    home: Union[float, int]
    away: Union[float, int]


class PastGameEvent(BaseModel):
    event_name: str
    time: int
    team: str
    player: str


class PastGameOverview(BaseModel):
    """
    Overview of past game result - info visible in general 'league-results' view only.
    Ex. view url: https://www.flashscore.com/football/england/premier-league/results/
    """
    datetime: datetime.datetime
    league: Optional[str]
    round: Optional[str]
    game_url: str
    home: str
    away: str
    goals_home: int
    goals_away: int


class GameDetailedOdds(BaseModel):
    odds_dc_home: float     # double chance 10 (home or draw)
    odds_dc_away: float     # double chance 02 (away or draw)
    odds_over_15: float     # over 1.5 goals
    odds_under_15: float    # under 1.5 goals
    odds_over_25: float     # over 2.5 goals
    odds_under_25: float    # under 2.5 goals
    odds_btts_yes: float    # both team to score
    odds_btts_no: float     # both team not to score


class PastGameDetails(BaseModel):
    """
    Details for past game - info visible in detailed match-summary view.
    Ex. summary view url: https://www.flashscore.com/match/WrqgEz5S/#/match-summary/match-summary
    """
    game_url: str
    league: str
    round: str
    datetime: datetime.datetime
    home: str
    away: str
    
    goals_home: int
    goals_away: int
    
    # odds_winner: float
    odds_home: float
    odds_draw: float
    odds_away: float
    
    odds: Optional[GameDetailedOdds]
    events: Optional[List[PastGameEvent]]
    stats: Optional[List[PastGameStat]]
    
    past_games_home: Optional[List[PastGameOverview]]
    past_games_away: Optional[List[PastGameOverview]]
    past_games_h2h: Optional[List[PastGameOverview]]

    referee: str
    attendance: int


class FutureGameOverview(BaseModel):
    """
    Overview of future games - info visible in general 'league-fixtures' view only.
    Ex. view url: https://www.flashscore.com/football/england/premier-league/fixtures/
    """
    datetime: datetime.datetime
    game_url: str
    home: str
    away: str


class FutureGameDetails(BaseModel):
    """
    Details for future game - info visible in detailed match-summary view.
    Ex. view url: https://www.flashscore.com/match/KndoYqyJ/#/match-summary 
    """
    game_url: str
    league: str
    round: str
    datetime: datetime.datetime
    home: str
    away: str

    referee: str
    
    odds_home: float
    odds_away: float
    odds_draw: float
    odds: Optional[GameDetailedOdds]
    
    past_games_home: Optional[List[Union[PastGameDetails, PastGameOverview]]]
    past_games_away: Optional[List[Union[PastGameDetails, PastGameOverview]]]
    past_games_h2h: Optional[List[Union[PastGameDetails, PastGameOverview]]]
    
    # post-game details:
    goals_home: Optional[int]
    goals_away: Optional[int]
    events: Optional[List[PastGameEvent]]
    stats: Optional[List[PastGameStat]]
    # odds_winner: Optional[float]
    attendance: Optional[int]