import os
from plugandcrawl import BasePipeline


class GameDetailsStats(BasePipeline):
    scenario = rf'{os.path.dirname(__file__)}/scenarios/game_stats.json'

    def __str__(self):
        return 'GameDetailsStats'

    async def prepare_page(self, page):
        await page.click('button#onetrust-reject-all-handler', required=False)
        await page.wait_for_timeout(3000)
        await page.click(".filterOver a[href*='/match-statistics']")
        await page.wait_for_timeout(3000)

    async def scrape_single_locator(self, locator):
        """
        Custom implementation - get stats for each split.
        """
        if locator['name'] == 'stats':
            splits = await self.page.locate_all_elements('.subFilterOver a')
            output = {}
            for split in splits:
                await split.click()
                title = await self.page.locate_one_element(selector=None, attr='text', root=split)
                stats = await super().scrape_single_locator(locator)
                output[title] = stats
            return output
        else:
            return await super().scrape_single_locator(locator)


game_stats_pipeline = GameDetailsStats()