from settings import settings
import utils as utils

from src.v0.base_pipelines import BasePipeline, overrides


class LeagueTable(BasePipeline):
    containers_selector = ".ui-table__row"
    container_fields = {
        "position": ".table__cell.table__cell--rank.table__cell--sorted::text",
        "team": ".tableCellParticipant__name::text",
        "team_url": ".tableCellParticipant__image::href",
        "games_played": "span[class=' table__cell table__cell--value   ']:nth-child(3)::text",
        "goals": ".table__cell.table__cell--value.table__cell--score::text",
        "goals_difference": "span[class*='table__cell--goalsForAgainstDiff']::text",
        "points": ".table__cell.table__cell--points::text",
        "team_form": ".table__cell.table__cell--form::text",
    }

    def __str__(self) -> str:
        return "standings"

    @staticmethod
    def process_position(value):
        return utils.parse_int(value.strip("."))
    
    @staticmethod
    def process_team_url(value):
        return f"https://www.flashscore.com{value}"
    
    @staticmethod
    def process_games_played(value):
        return utils.parse_int(value)
    
    @staticmethod
    def process_goals(value):
        return {
            "scored": utils.parse_int(value.split(":")[0]),
            "conceded": utils.parse_int(value.split(":")[1])
        }

    @staticmethod
    def process_goals_difference(value):
        return utils.parse_int(value)
    
    @staticmethod
    def process_points(value):
        return utils.parse_int(value)
    
    @staticmethod
    def process_team_form(value):
        return [el for el in value.strip("?")]
    

league_table_pipeline = LeagueTable()