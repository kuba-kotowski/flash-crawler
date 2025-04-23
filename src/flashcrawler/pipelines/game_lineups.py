import os
from plugandcrawl import BasePipeline


class GameDetailsLineups(BasePipeline):
    scenario = rf'{os.path.dirname(__file__)}/scenarios/game_lineups.json'

    def __str__(self):
        return 'GameDetailsLineups'

    async def prepare_page(self, page):
        await page.click(".filterOver a[href*='/lineups']")
        await page.wait_for_timeout(1000)

    @staticmethod
    def process_name(value):
        return value.replace('(G)', '').replace('(C)', '').strip()

    @staticmethod
    def process_role(value):
        """ Extracts roles from the player name."""
        roles = []
        if value.find('(G)') != -1:
            roles.append('goalkeeper')
        elif value.find('(C)') != -1:
            roles.append('captain')
        return roles

    @staticmethod
    def process_url(value):
        return f"https://www.flashscore.com{value}"

    @staticmethod
    def process_side(value):
        # Based on the class name - on the right side there are away players/coach
        if value.find('lf__isReversed') != -1:
            return 'away'
        return 'home'

    @staticmethod
    def get_additional_player_fields(player, players):
        """
        Gets additional player information based from the players list.
        """
        for p in players:
            # player name can be a substring of the name in the list
            if p['name'] == player['name'] or p['name'] in player['name'] or player['name'] in p['name']:
                return {
                    'name': p.get('name'), # get extended name, on the pitch it can be shortened
                    'side': p.get('side'),
                    'country': p.get('country'),
                    'number': p.get('number'),
                    'role': p.get('role'),
                }
        return {}

    @staticmethod
    def clean_player(player):
        player.pop('side', None)
        keys_order = ['name', 'country', 'url', 'number'] # rest at the end
        all_keys = [k for k in keys_order if k in player.keys()]+[k for k in player.keys() if k not in keys_order]
        return {k: player.get(k) for k in all_keys}

    async def run(self, *args, **kwargs):
        output = await super().run(*args, **kwargs)
        
        home, away = {}, {}
        for idx, side in enumerate([home, away]):
            fields = ['formations', 'team_ratings', 'coaches']
            for field in fields:
                if len(output.get(field, [])) != 2:
                    raise ValueError(f"Invalid number of {field}: {output.get(field)}")

            side.update({
                'formation': output.get('formations')[idx].replace(' ', ''),
                'team_rating': output.get('team_ratings')[idx],
                'coach': output.get('coaches')[idx]
            })

        players = output.get('players', [])
        start_lineup = output.get('pitch_lineups', [])
        substitutes = output.get('substitutes', []) 
        
        for starting_player in start_lineup:
            starting_player.update(self.get_additional_player_fields(starting_player, players))

        for substitute_player in substitutes:
            substitute_player.update(self.get_additional_player_fields(substitute_player, players))

        pitch_player_names = [p.get('name') for p in start_lineup+substitutes]
        bench_players = [p for p in players if p.get('name') not in pitch_player_names]

        for side in [(home, 'home'), (away, 'away')]:
            side_starting = [self.clean_player(p) for p in start_lineup if p.get('side') == side[1]]
            side_substitutes = [self.clean_player(p) for p in substitutes if p.get('side') == side[1]]
            side_bench = [self.clean_player(p) for p in bench_players if p.get('side') == side[1]]
            side_missing = [self.clean_player(p) for p in output.get('missing_players', []) if p.get('side') == side[1]]

            side[0].update(
                {
                    'players': {
                        'starting': side_starting.copy(),
                        'substitutes': side_substitutes.copy(),
                        'bench': side_bench.copy(),
                        'missing': side_missing.copy()
                    }
                }
            )
            side[0].get('coach').pop('side', None)
        
        return {
            'home': home,
            'away': away
        }

game_lineups_pipeline = GameDetailsLineups()