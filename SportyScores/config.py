import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

ESPN_API_URLS = {
    'nfl': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
    'mlb': 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard',
    'nba': 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
    'nhl': 'https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard'
}

UPDATE_INTERVAL = 30

LEAGUE_COLORS = {
    'nfl': 0x013369,
    'mlb': 0x041E42,
    'nba': 0x1D428A,
    'nhl': 0x000000
}

LEAGUE_NAMES = {
    'nfl': 'NFL',
    'mlb': 'MLB',
    'nba': 'NBA',
    'nhl': 'NHL'
}
