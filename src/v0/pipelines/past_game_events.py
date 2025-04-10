from settings import settings
import utils as utils

from src.v0.base_pipelines import BasePipeline, overrides


class PastGameEvents(BasePipeline):
    url_suffix = "/#/match-summary/match-summary"
    containers_selector = ".smv__verticalSections.section .smv__participantRow, .smv__incidentsHeader.section__title" # includes sections delimiter (output is split by sections)
    container_fields = {
        "event_name": "div[class*='smv__incidentIcon'] svg::class || div[class*='smv__incidentIcon'] svg::data-testid || > div:nth-child(1)::text",
        "event_time": ".smv__timeBox::text",
        "team": "::class",
        "player": ".smv__incident > a.smv__playerName::text",
        "event_details": ".smv__subDown.smv__playerName, .smv__subIncident, .smv__assist::text"
    }
    
    def __str__(self) -> str:
        return "past_game_events"

    @overrides(BasePipeline)
    async def prepare_page(self, driver, page):
        await driver.sleep(page=page, sec=1)

    @staticmethod
    def process_event_name(name: str) -> str:
        map_dict = {
            "yellowCard": "yellow_card",
            "redCard": "red_card",
            "card-ico": "yellow_red_card",
            "footballOwnGoal-ico": "own_goal",
            "wcl-icon-soccer": "goal"
        }
        if not name:
            return "unknown"
        for key, value in map_dict.items():
            if key in name:
                return value
        return name.lower().strip()
    
    @staticmethod
    def process_event_time(time: str) -> int:
        if time and time.find("'") != -1:
            return utils.parse_int(time.split("+")[0].replace("'", ""))
        else:
            return None
    
    @staticmethod
    def process_team(team: str) -> str:
        if "home" in team:
            return "home"
        elif "away" in team:
            return "away"
        elif "section__title" in team:
            return "section"
        else:
            return "-"
    
    @staticmethod
    def process_event_details(description: str) -> str:
        if isinstance(description, list):
            return " ".join(description).strip()
        if description:
            return str(description).strip("()")
        else:
            return "-"

    @overrides(BasePipeline)
    def prepare_output(self, output: list) -> list:
        """Getting the section names for the events. Sections are '1H', '2H', 'Extra Time', 'Penalties' etc."""
        sections = [(idx, event.get("event_name")) for idx, event in enumerate(output) if event.get("team") == "section"]
        
        def get_section(sections: tuple, idx: int):
            """Returns the section name of the event for the given index"""
            # [section, event, event, event ... , section2, event, event, event ...] 
            # |=> getting the last section which index is lower than the current event index
            return [section[1] for section in sections if idx >= section[0]][-1]
        
        [event.update({"section": get_section(sections, idx)}) for idx, event in enumerate(output) if event.get("team") != "section"]
        return [event for event in output if event.get("team") != "section"]
