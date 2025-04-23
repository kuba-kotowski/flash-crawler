import json
import asyncio

import pipelines
from plugandcrawl import BasePipelinesManager


def save_output(output):
    with open('output.json', 'w') as f:
        f.write(json.dumps(output))


def on_error(input, e):
    print(f"Error in {input}: {e}")


pipelines_manager = BasePipelinesManager()
pipelines_manager.pipelines=[
    pipelines.game_details_pipeline,
    pipelines.game_events_pipeline,
    pipelines.game_stats_pipeline,
    pipelines.game_lineups_pipeline,
]

pipelines_manager.post_all_urls = save_output
pipelines_manager.on_error = on_error


if __name__ == '__main__':
    input_data = [
        {'url': "https://www.flashscore.com/match/80d4l8PF/"}
    ]
    asyncio.run(
        pipelines_manager.run(
            input_data=input_data,
            headless=False
        )
    )