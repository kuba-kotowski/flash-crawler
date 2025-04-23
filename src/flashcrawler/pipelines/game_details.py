import os
from plugandcrawl import BasePipeline


def parse_team_url(value):
    return f"https://www.flashscore.com{value}"


game_details_pipeline = BasePipeline()

game_details_pipeline.scenario = rf'{os.path.dirname(__file__)}/scenarios/game_details.json'

# parsing method for field 'round':
game_details_pipeline.process_round = lambda value: value.split('-', 1)[-1].strip()

# parsing method for field 'home_ur':
game_details_pipeline.process_home_url = parse_team_url 

# parsing method for field 'away_url':
game_details_pipeline.process_away_url = parse_team_url