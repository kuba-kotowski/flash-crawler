import os
from plugandcrawl import BasePipeline


class GameDetailsEvents(BasePipeline):
    scenario = rf'{os.path.dirname(__file__)}/scenarios/game_events.json'

    def __str__(self):
        return 'GameDetailsEvents'

    async def prepare_page(self, page):
        await page.click('button#onetrust-reject-all-handler', required=False)
        await page.wait_for_timeout(3000)
        await page.click(".filterOver a[href*='match-summary/match-summary']")
        await page.wait_for_timeout(3000)

    @staticmethod
    def process_additional_info(value):
        return value.strip('()')

    async def run(self, *args, **kwargs):
        output = await super().run(*args, **kwargs)
        
        split_output = {}
        last_split = None
        for event in output:
            if event.get('header'):
                last_split = event['header']
                split_output[last_split] = []
            elif last_split:
                event.pop('header', None)
                split_output[last_split].append(event)
        return split_output


game_events_pipeline = GameDetailsEvents()