from pipelines.past_game_details import PastGameOverview
from pipelines.past_game_events import PastGameEvents
from pipelines.past_game_stats import PastGameStatistics
from pipelines.game_odds import DetailedOdds

from src.v0.webdriver import Webdriver


async def run():
    async with Webdriver(headless=False) as driver:
        url = "https://www.flashscore.com/match/80d4l8PF/"
        context = await driver.new_context()
        output = await asyncio.gather(
            PastGameOverview().run(driver=driver, url=url, context=context),
            PastGameEvents().run(driver=driver, url=url, context=context),
            PastGameStatistics().run(driver=driver, url=url, context=context),
            DetailedOdds().run(driver=driver, url=url, context=context)
        )
        print(output)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())

