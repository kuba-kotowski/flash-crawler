import re
from datetime import datetime, date
from typing import Dict, List, Tuple


def update_past_game_details(past_game: Dict) -> Dict:
    output = past_game.copy()
    output.update({
        "datetime": process_datetime(output["datetime"]),
        "league": process_league(output["league"])[0],
        "round": process_league(output["league"])[1],
        "referee": process_ref(output["referee"]),
        "attendance": process_attendance(output["attendance"])
    })
    return output


def update_future_game_details(future_game: Dict) -> Dict:
    output = future_game.copy()
    output.update({
        "datetime": process_datetime(output["datetime"]),
        "league": process_league(output["league"])[0],
        "round": process_league(output["league"])[1],
        "referee": process_ref(output["referee"])
    })
    return output


def process_datetime(d: str) -> datetime:
    if not re.findall("[0-9]{2}\.[0-9]{2}\.[0-9]{2}", d):
        short_date = re.findall("[0-9]{2}\.[0-9]{2}\.", d)[0]
        d = d.replace(short_date, f"{short_date}{date.today().year}")
    try:
        return datetime.strptime(d, "%d.%m.%Y %H:%M")
    except: 
        return datetime(1, 1, 1, 1, 1, 1)


def process_ref(ref: str) -> str:
    if ref:
        return ref.replace("Referee:", "").strip()
    else:
        return "-"


def process_attendance(attendance: str) -> int:
    if attendance:
        return int(re.sub("[Attendance:| ]", "", attendance))
    else:
        return 0


def process_league(string: str) -> Tuple[str, str]:
    league = re.sub("\([A-z]*\)", "", string).strip()
    if "-" in league:
        return league.split("-", 1)[0], league.split("-", 1)[1] 
    else:
        return league, "-" 


def process_stat(stat: Dict) -> Dict:
    stat_output = {
        "stat_name": re.sub("[ |-]", "_", stat["stat_name"].lower()),
        "home": process_stat_value(stat["home"]),
        "away": process_stat_value(stat["away"])
    }
    return stat_output


def process_stat_value(value: str) -> int:
    if "%" not in value:
        return int(value)
    else:
        return int(value.replace("%", ""))/100


def process_event(event: Dict) -> Dict:
    event_output = {
        "event_name": process_event_name(event["event_name"]),
        "time": process_event_time(event["time"]),
        "team": process_event_team(event["team"]),
        "player": event["player"]
    }
    return event_output


def process_event_name(name: str) -> str:
    if "yellowCard" in name:
        return "yellow_card"
    elif "redCard" in name:
        return "red_card"
    elif "card-ico" in name:
        return "yellow_red_card"
    else:
        return name.replace("soccer", "goal")


def process_event_time(time: str) -> int:
    time = time.replace("'", "")
    if "+" not in time:
        return int(time)
    else:
        return int(time.split("+")[0])+int(time.split("+")[1])


def process_event_team(team: str) -> str:
    if "home" in team:
        return "home"
    elif "away" in team:
        return"away"
    else:
        return "-"


def filter_odds_over_under(odds: List[Dict]) -> Dict:
    odds15 = [element for element in odds if element["goals"]=="1.5"][0]
    output = {
        "odds_over_15": odds15["over"],
        "odds_under_15": odds15["under"]
        }
    odds25 = [element for element in odds if element["goals"]=="2.5"][0]
    output.update({
        "odds_over_25": odds25["over"],
        "odds_under_25": odds25["under"]
        })    
    return output
