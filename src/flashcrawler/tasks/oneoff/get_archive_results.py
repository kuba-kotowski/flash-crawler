import os

from plugandcrawl import BasePipelinesManager

from ...pipelines import results_pipeline
from ...utils.save import save_to_s3, create_s3_client


class ArchiveResultsTask:
    s3_uri = 's3://flashcrawler/past-results-urls/'

    def __init__(self):
        self.s3_client = create_s3_client(
            access_key=os.getenv('AWS_ACCESS_KEY_ID'),
            secret_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

        self.pipeline_manager = BasePipelinesManager()
        self.pipeline_manager.pipelines = [results_pipeline]
        self.pipeline_manager.post_single_url = self.save_results

    @staticmethod
    def create_input_data():
        leagues = [
            'italy/serie-a',
            'germany/bundesliga',
            'spain/laliga',
            'england/premier-league',
            'france/ligue-1',
        ]
        seasons = [
            '2023-2024',
            '2022-2023',
            '2021-2022',
            '2020-2021',
            '2019-2020',
            '2018-2019',
            '2017-2018',
        ]
        return [{'url': f'https://www.flashscore.com/football/{league}-{season}/results/'} for league in leagues for season in seasons]

    def save_results(self, data):
        """
        data: {
            'season': '2023-2024',
            'league': 'Serie A',
            'results': [
                {
                    'url': 'https://www.flashscore.com/football/italy/serie-a/results/',
                    'home_team': 'AC Milan',
                    'away_team': 'Inter Milan',
                    # ... other fields
                },
                # ... more results
            ]
        }
        """
        season = data.get('season').replace('/', '_')
        league = data.get('league').lower().replace(' ', '_')
        urls = data.get('results')

        save_to_s3(
            data = urls,
            s3_client = self.s3_client,
            s3_uri = self.s3_uri + f'{league}/{league}_{season}.json'
        )

        print(f"Saved results for {league} {season}. ({len(urls)} URLs)")
    
    async def run(self, headless, workers=1):
        self.pipeline_manager.workers = workers
        
        await self.pipeline_manager.run(
            input_data = self.create_input_data(),
            headless = headless,
        )

task = ArchiveResultsTask()
