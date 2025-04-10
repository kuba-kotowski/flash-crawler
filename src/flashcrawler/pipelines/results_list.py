import os
from plugandcrawl import BasePipeline


async def prepare_page(page):
    await page.click('button#onetrust-reject-all-handler', required=False)
    while True:
        try:
            await page.click('.event__more.event__more--static', required=True)
            await page.wait_for_timeout(1000)
        except:
            break
    await page.wait_for_timeout(1000)


results_pipeline = BasePipeline()

results_pipeline.scenario = rf'{os.path.dirname(__file__)}/scenarios/results_list.json'

results_pipeline.prepare_page = prepare_page
