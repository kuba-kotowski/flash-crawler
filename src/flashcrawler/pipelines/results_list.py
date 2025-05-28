import os
from plugandcrawl import BasePipeline


scenario_path = os.path.dirname(__file__) + '/scenarios/results_list.json'

results_pipeline = BasePipeline.from_json(scenario_path)


async def prepare_page(page):
    await page.click('button#onetrust-reject-all-handler', required=False)
    await page.click('.langBoxSetup__button.langBoxSetup__button--stayBtn', required=False)

    while True:
        try:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(1000)
            await page.click('.event__more.event__more--static', required=True)
            await page.wait_for_timeout(1000)
        except:
            break

results_pipeline.prepare_page = prepare_page
