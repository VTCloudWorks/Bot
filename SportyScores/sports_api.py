import aiohttp
from typing import Dict, List, Optional
from config import ESPN_API_URLS

class SportsAPI:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def create_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def fetch_scores(self, league: str) -> Optional[Dict]:
        if league not in ESPN_API_URLS:
            return None
        
        await self.create_session()
        
        try:
            async with self.session.get(ESPN_API_URLS[league]) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            print(f"Error fetching {league.upper()} scores: {e}")
            return None
    
    def parse_games(self, data: Dict, league: str) -> List[Dict]:
        if not data or 'events' not in data:
            return []
        
        games = []
        for event in data['events']:
            try:
                competition = event['competitions'][0]
                status = competition['status']
                competitors = competition['competitors']
                
                home_team = next((c for c in competitors if c['homeAway'] == 'home'), None)
                away_team = next((c for c in competitors if c['homeAway'] == 'away'), None)
                
                if not home_team or not away_team:
                    continue
                
                linescores_home = home_team.get('linescores', [])
                linescores_away = away_team.get('linescores', [])
                
                venue = competition.get('venue', {})
                venue_name = venue.get('fullName', 'TBD')
                
                broadcast = competition.get('broadcasts', [{}])[0].get('names', ['Not Available'])[0] if competition.get('broadcasts') else 'Not Available'
                
                odds = competition.get('odds', [{}])[0] if competition.get('odds') else {}
                
                home_stats = home_team.get('statistics', [])
                away_stats = away_team.get('statistics', [])
                
                situation = competition.get('situation', {})
                
                game_info = {
                    'id': event['id'],
                    'league': league,
                    'name': event.get('name', ''),
                    'short_name': event.get('shortName', ''),
                    'home_team': home_team['team']['displayName'],
                    'away_team': away_team['team']['displayName'],
                    'home_team_id': home_team['team'].get('id', ''),
                    'away_team_id': away_team['team'].get('id', ''),
                    'home_team_abbr': home_team['team'].get('abbreviation', ''),
                    'away_team_abbr': away_team['team'].get('abbreviation', ''),
                    'home_team_logo': home_team['team'].get('logo', ''),
                    'away_team_logo': away_team['team'].get('logo', ''),
                    'home_team_color': home_team['team'].get('color', '000000'),
                    'away_team_color': away_team['team'].get('color', '000000'),
                    'home_score': home_team['score'],
                    'away_score': away_team['score'],
                    'home_linescores': linescores_home,
                    'away_linescores': linescores_away,
                    'status': status['type']['description'],
                    'detail': status['type']['detail'],
                    'completed': status['type']['completed'],
                    'period': status.get('period', 0),
                    'clock': status.get('displayClock', ''),
                    'home_record': home_team.get('records', [{}])[0].get('summary', ''),
                    'away_record': away_team.get('records', [{}])[0].get('summary', ''),
                    'venue': venue_name,
                    'broadcast': broadcast,
                    'odds_details': odds.get('details', ''),
                    'overunder': odds.get('overUnder', ''),
                    'home_stats': home_stats,
                    'away_stats': away_stats,
                    'situation': situation,
                    'attendance': competition.get('attendance', 0)
                }
                
                games.append(game_info)
            except (KeyError, IndexError) as e:
                print(f"Error parsing game data: {e}")
                continue
        
        return games
