from settings import settings
import utils as utils

from src.v0.base_pipelines import BasePipeline, overrides


class PastGameOverview(BasePipeline):
    url_suffix = "/#/match-summary/match-summary"
    fields = {
        "game_url": "{current_url}",
        "datetime": ".duelParticipant__startTime::text",
        "league": ".tournamentHeader__country a::text",
        "home": ".duelParticipant__home a.participant__participantName::text",
        "home_url": ".duelParticipant__home a.participant__participantName::href",
        "away": ".duelParticipant__away a.participant__participantName::text",
        "away_url": ".duelParticipant__away a.participant__participantName::href",
        "goals_home": ".duelParticipant__score .detailScore__wrapper span:nth-child(1)::text",
        "goals_away": ".duelParticipant__score .detailScore__wrapper span:nth-child(3)::text",
        "additional_details": "[class^='_infoLabelWrapper'], [class^='_infoValue']::text"
    }

    @staticmethod
    def process_game_url(value):
        return utils.parse_base_url(value)

    @staticmethod
    def process_datetime(value):
        return utils.parse_datetime(value, '%d.%m.%Y %H:%M')
    
    @staticmethod
    def process_league(value):
        return utils.parse_league(value)

    @staticmethod
    def process_home_url(value):
        return f"https://www.flashscore.com{value}"
    
    @staticmethod
    def process_away_url(value):
        return f"https://www.flashscore.com{value}"
    
    @staticmethod
    def process_goals_home(value):
        return utils.parse_int(value)

    @staticmethod
    def process_goals_away(value):
        return utils.parse_int(value)

    @staticmethod
    def process_additional_details(value):
        if isinstance(value, list):
            details = {value[i].lower().replace(" ", "_").strip(":"): value[i+1].strip().replace("\xa0", " ") for i in range(0, len(value), 2)}
            for k, v in details.items():
                if k == "attendance" or k == "capacity":
                    details[k] = utils.parse_int(v.replace(" ", "").strip())
            return details
        return value

    @overrides(BasePipeline)
    async def prepare_page(self, driver, page, **kwargs):
        await driver.sleep(page=page, sec=2)
