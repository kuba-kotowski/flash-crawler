import os
from plugandcrawl import BasePipeline


class GameDetailsEvents(BasePipeline):
    scenario = rf'{os.path.dirname(__file__)}/scenarios/game_events.json'

    async def prepare_page(self, page):
        await page.click(".filterOver a[href*='match-summary/match-summary']")
        await page.wait_for_timeout(1000)

    @staticmethod
    def process_additional_info(value):
        return value.strip('()')

    async def run(self, *args, **kwargs):
        output = await super().run(*args, **kwargs)
        
        split_output = {}
        last_split = None
        for event in output.get(str(self)):
            if event.get('header'):
                last_split = event['header']
                split_output[last_split] = []
            elif last_split:
                event.pop('header', None)
                split_output[last_split].append(event)
        return {str(self): split_output}


game_events_pipeline = GameDetailsEvents()