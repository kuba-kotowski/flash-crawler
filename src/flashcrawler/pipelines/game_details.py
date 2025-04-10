import os
from plugandcrawl import BasePipeline


class GameDetails(BasePipeline):
    scenario = rf'{os.path.dirname(__file__)}/scenarios/game_details.json'

    def __str__(self):
        return 'GameDetails'

    async def prepare_page(self, page):
        await page.click('button#onetrust-reject-all-handler', required=False)

    @staticmethod
    def process_home_url(value):
        return f"https://www.flashscore.com{value}"
    
    @staticmethod
    def process_away_url(value):
        return f"https://www.flashscore.com{value}"


game_details_pipeline = GameDetails()