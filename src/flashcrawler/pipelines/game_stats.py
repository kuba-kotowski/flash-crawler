import os
from plugandcrawl import BasePipeline


class GameDetailsStats(BasePipeline):
    scenario = rf'{os.path.dirname(__file__)}/scenarios/game_stats.json'

    async def prepare_page(self, page):
        await page.click(".filterOver a[href*='/match-statistics']")
        await page.wait_for_timeout(1000)

    async def scrape_single_locator(self, page, locator):
        """
        Custom implementation - get stats for each split.
        """
        if locator['name'] == 'stats':
            splits = await page.locate_all_elements('.subFilterOver a')
            output = {}
            for split in splits:
                await split.click()
                title = await page.locate_one_element(selector=None, attr='text', root=split)
                stats = await super().scrape_single_locator(page, locator)
                output[title] = stats
            return {str(self): output}
        else:
            return await super().scrape_single_locator(page, locator)


game_stats_pipeline = GameDetailsStats()