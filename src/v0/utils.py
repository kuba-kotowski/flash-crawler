from datetime import datetime
import re


def parse_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def parse_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0.0


def parse_datetime(d: str, format: str) -> datetime:
    if d:
        try:
            return datetime.strptime(d, format)
        except Exception as e:
            print("Parsing datetime error:", e)
            return None
    else:
        return None


def parse_league(value: str):
    league = re.sub("\([A-z]*\)", "", value).strip()
    if "-" in league:
        return {"league": league.split("-", 1)[0].strip(), "round": league.split("-", 1)[1].strip()}
    else:
        return {"league": league, "round": "-"}


def parse_base_url(value: str):
    return value.replace("/#/match-summary/match-summary", "").replace("/#/match-summary", "")


def get_days_diff(d1: datetime, d2: datetime) -> bool:
    if type(d1) == datetime and type(d2) == datetime:
        return (d1-d2).days
    else:
        return None


def runtime(func):
    async def wrapper(*args, **kwargs):
        start = datetime.now()
        result = await func(*args, **kwargs)
        print(f"Function {func.__name__} took {datetime.now()-start} to run")
        return result
    return wrapper


# async def get_cutoff_id_by_last_n_days(driver, url: str, last_n_days: int = 7) -> str:
#     """Returns the container id of the given datetime"""
#     # season_selector = ".heading__info::text"
#     containers_selector = ".event__match"
#     container_fields = {
#         "datetime": ".event__time::text" # latest dates are in format 'dd-mm hh:mm'
#     }

#     page, context = await driver.new_page()
#     await driver.navigate_to(page=page, url=url)
#     # season = await driver.get_one_field(page=page, field_name="season", selector=season_selector).get("season")
#     # if season and season.find("/") != -1:
#     #     season_start, season_end = season.split("/")

#     # containers_fields = await driver.get_all_containers_fields(
#     #     page=page, 
#     #     container_selector=containers_selector, 
#     #     fields=container_fields
#     # )
#     # gametimes = [parse_datetime(container_fields.get("datetime"), "%d.%m. %H:%M") for container_fields in containers_fields]
#     # for idx, gametime in enumerate(gametimes):
#     #     if gametime.month <= 12 and gametime.month > 7:
#     #         gametime = gametime.replace(year=int(season_start))
#     #     else:
#     #         gametime = gametime.replace(year=int(season_end))
        

#     # gametimes = [gametime.replace(year=datetime.now().year) if gametime and gametime.month > 6 else None for gametime in gametimes]
    
#     # for idx, date in enumerate(game_times):
#     #     date_to_compare = parse_datetime(gametime, "%Y-%m-%d")
#     #     print(compare_datetime(date, date_to_compare))

#     containers = await driver.locate_many_elements(page=page, selector=containers_selector)
#     for idx, container in enumerate(containers):
#         container_fields = await driver.handle_popup(page=container, context=context, popup_selector="", fields=container_fields)
#         gametime = parse_datetime(container_fields.get("datetime"), "%d.%m. %H:%M")
#         print(gametime)
#         if gametime:
#             if get_days_diff(datetime.now(), gametime) < last_n_days:
#                 return idx


# if __name__ == "__main__":
#     from settings import settings
#     from src.webdriver import Webdriver
#     from playwright.async_api import async_playwright
#     import asyncio

#     async def main():
#         async with async_playwright() as async_pl:
#             driver = await Webdriver.init(async_pl, headless=False)
#             url = "https://www.flashscore.com/football/england/premier-league/results/"
#             print(await get_cutoff_id_by_last_n_days(driver, url))

#     asyncio.run(main())