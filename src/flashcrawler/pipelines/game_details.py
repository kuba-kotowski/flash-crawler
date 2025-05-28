import os
from plugandcrawl import BasePipeline


scenario_path = os.path.dirname(__file__) + '/scenarios/game_details.json'

game_details_pipeline = BasePipeline.from_json(scenario_path)


# parsing method for field 'round':
def parse_round(value):
    return value.split('-', 1)[-1].strip()

game_details_pipeline.process_round = parse_round


# parsing method for field 'home_ur' & 'away_url':
def parse_team_url(value):
    return f"https://www.flashscore.com{value}"

game_details_pipeline.process_home_url = parse_team_url 
game_details_pipeline.process_away_url = parse_team_url