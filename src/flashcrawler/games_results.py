import asyncio
import json

import pipelines
from plugandcrawl import BasePipelinesManager

def save_output(output):
    with open('output.json', 'w') as f:
        f.write(json.dumps(output))

pipelines_manager = BasePipelinesManager(workers=3)

pipelines_manager.pipelines = [pipelines.results_pipeline]

pipelines_manager.post_all_urls = save_output


if __name__ == '__main__':
    input_data = [
        {'url': 'https://www.flashscore.com/football/italy/serie-a/results/'}
    ]
    asyncio.run(
        pipelines_manager.run(
            input_data=input, 
            headless=False
        )
    )