import os

from plugandcrawl import BasePipelinesManager

from ...pipelines import game_details_pipeline, game_stats_pipeline, game_events_pipeline, game_lineups_pipeline
from ...utils.save import save_to_s3, create_s3_client


class GameDetailsTask:
    s3_uri = 's3://flashcrawler/game-details/'

    def __init__(self):
        self.s3_client = create_s3_client(
            access_key=os.getenv('AWS_ACCESS_KEY_ID'),
            secret_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

        self.pipeline_manager = BasePipelinesManager()
        self.pipeline_manager.pipelines = [
            game_details_pipeline,
            game_stats_pipeline,
            game_events_pipeline,
            game_lineups_pipeline,
        ]
        self.pipeline_manager.on_error = self.on_error # DONT WORK AND LINEUPS THROWS ERROR PROBABLY?
        # self.pipeline_manager.post_single_url = self.save_results
        self.pipeline_manager.post_single_url = print

    @staticmethod
    def on_error(input, error):
        print(error)

    def save_results(self, data):
        """
        data: {
            'season': '2023-2024',
            'league': 'Serie A',
            
            'datetime': '20.05.2018 20:45'
            'round': 'Serie A - Round 38',
            'home': 'Juventus',
            'away': 'AC Milan',
            'Stats': {
                'Match': [...]
            }
            'Events': {
                'Match': [...]
            },
        }
        """
        save_to_s3(
            data = data,
            s3_client = self.s3_client,
            s3_uri = self.s3_uri + 
                f"{data.get('league', 'not-found')}/{data.get('season', 'not-found')}/{data.get('round', 'not-found')}/{data['home']}-{data['away']}.json"
        )
    
    async def run(self, headless, workers=1):
        self.pipeline_manager.workers = workers
        
        await self.pipeline_manager.run(
            input_data = {
                'url': 'https://www.flashscore.com/match/football/nLvvWCPs/#/match-summary/match-summary', 
                'season': '2023-2024',
                'league': 'Serie A'
            },
            headless = headless,
        )

task = GameDetailsTask()
