import discord
from discord.ext import commands
from typing import Dict, List
from config import LEAGUE_COLORS, LEAGUE_NAMES

class GameTracker:
    def __init__(self):
        self.tracked_messages: Dict[str, Dict] = {}
    
    def add_tracked_message(self, game_id: str, message: discord.Message, league: str):
        self.tracked_messages[game_id] = {
            'message': message,
            'league': league,
            'last_score': None
        }
    
    def remove_tracked_message(self, game_id: str):
        if game_id in self.tracked_messages:
            del self.tracked_messages[game_id]
    
    def get_tracked_games(self) -> Dict[str, Dict]:
        return self.tracked_messages
    
    def update_last_score(self, game_id: str, score: str):
        if game_id in self.tracked_messages:
            self.tracked_messages[game_id]['last_score'] = score

def create_game_embed(game: Dict, league: str, bot_user=None) -> discord.Embed:
    color = LEAGUE_COLORS.get(league, 0x000000)
    league_name = LEAGUE_NAMES.get(league, league.upper())
    
    try:
        team_color = f"0x{game['home_team_color']}" if game.get('home_team_color') else None
        if team_color and len(game['home_team_color']) == 6:
            color = int(game['home_team_color'], 16)
    except:
        pass
    
    title = f"🏟️ {game['away_team']} vs {game['home_team']}"
    
    status_emoji = "🔴 LIVE" if not game['completed'] and game['period'] > 0 else ("✅ FINAL" if game['completed'] else "⏰ SCHEDULED")
    
    description = f"**{league_name}** | {status_emoji}\n{game['detail']}"
    
    embed = discord.Embed(
        title=title,
        color=color,
        description=description,
        url=f"https://www.espn.com/{league}/game/_/gameId/{game['id']}"
    )
    
    if bot_user:
        embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=bot_user.display_avatar.url
        )
    
    if game.get('away_team_logo'):
        embed.set_thumbnail(url=game['away_team_logo'])
    
    score_breakdown = format_score_breakdown(game, league)
    embed.add_field(name="📊 Score", value=score_breakdown, inline=False)
    
    if game['period'] > 0 and not game['completed']:
        period_name = get_period_name(league, game['period'])
        clock_info = f"**{period_name}**"
        if game['clock']:
            clock_info += f" | ⏱️ {game['clock']}"
        embed.add_field(name="🕐 Game Clock", value=clock_info, inline=True)
    
    if game.get('situation') and league in ['nfl', 'mlb']:
        situation_text = format_situation(game['situation'], league, game)
        if situation_text:
            embed.add_field(name="📍 Current Situation", value=situation_text, inline=True)
    
    if game['home_record'] or game['away_record']:
        records = ""
        if game['away_record']:
            records += f"**{game['away_team_abbr']}:** {game['away_record']}\n"
        if game['home_record']:
            records += f"**{game['home_team_abbr']}:** {game['home_record']}"
        if records:
            embed.add_field(name="📈 Season Records", value=records, inline=True)
    
    venue_broadcast = []
    if game.get('venue') and game['venue'] != 'TBD':
        venue_broadcast.append(f"🏟️ **Venue:** {game['venue']}")
    if game.get('broadcast') and game['broadcast'] != 'Not Available':
        venue_broadcast.append(f"📺 **TV:** {game['broadcast']}")
    if game.get('attendance') and game['attendance'] > 0:
        venue_broadcast.append(f"👥 **Attendance:** {game['attendance']:,}")
    
    if venue_broadcast:
        embed.add_field(name="📍 Game Info", value="\n".join(venue_broadcast), inline=False)
    
    if game.get('odds_details') or game.get('overunder'):
        odds_info = []
        if game.get('odds_details'):
            odds_info.append(f"💰 **Line:** {game['odds_details']}")
        if game.get('overunder'):
            odds_info.append(f"📉 **O/U:** {game['overunder']}")
        if odds_info:
            embed.add_field(name="🎲 Betting Lines", value="\n".join(odds_info), inline=True)
    
    if game.get('home_team_logo'):
        embed.set_image(url=game['home_team_logo'])
    
    footer_text = f"Blazed A.I • Game ID: {game['id']}"
    embed.set_footer(
        text=footer_text,
        icon_url=bot_user.display_avatar.url if bot_user else None
    )
    embed.timestamp = discord.utils.utcnow()
    
    return embed

def format_score_breakdown(game: Dict, league: str) -> str:
    away_score = game['away_score']
    home_score = game['home_score']
    away_team = game['away_team_abbr'] or game['away_team'][:3].upper()
    home_team = game['home_team_abbr'] or game['home_team'][:3].upper()
    
    score_display = f"```\n"
    
    if game.get('away_linescores') and len(game['away_linescores']) > 0:
        period_labels = []
        if league == 'nfl':
            period_labels = ['Q1', 'Q2', 'Q3', 'Q4'] + [f'OT{i}' for i in range(1, 6)]
        elif league == 'nba':
            period_labels = ['Q1', 'Q2', 'Q3', 'Q4'] + [f'OT{i}' for i in range(1, 6)]
        elif league == 'nhl':
            period_labels = ['P1', 'P2', 'P3', 'OT', 'SO']
        elif league == 'mlb':
            period_labels = [f'{i}' for i in range(1, 20)]
        
        header = f"{'Team':<6}"
        for i, _ in enumerate(game['away_linescores']):
            if i < len(period_labels):
                header += f" {period_labels[i]:>3}"
        header += f" {'Total':>5}"
        score_display += f"{header}\n"
        score_display += f"{'-' * len(header)}\n"
        
        away_line = f"{away_team:<6}"
        for score in game['away_linescores']:
            away_line += f" {score.get('value', '-'):>3}"
        away_line += f" {away_score:>5}"
        score_display += f"{away_line}\n"
        
        home_line = f"{home_team:<6}"
        for score in game['home_linescores']:
            home_line += f" {score.get('value', '-'):>3}"
        home_line += f" {home_score:>5}"
        score_display += f"{home_line}\n"
    else:
        score_display += f"{away_team:<6} {away_score:>5}\n"
        score_display += f"{home_team:<6} {home_score:>5}\n"
    
    score_display += "```"
    return score_display

def format_situation(situation: Dict, league: str, game: Dict = None) -> str:
    if not situation:
        return ""
    
    if league == 'nfl':
        parts = []
        if situation.get('possession'):
            possession_id = str(situation['possession'])
            possession_team = "Unknown"
            
            if game:
                if possession_id == str(game.get('home_team_id')):
                    possession_team = game.get('home_team_abbr', game.get('home_team', 'Unknown'))
                elif possession_id == str(game.get('away_team_id')):
                    possession_team = game.get('away_team_abbr', game.get('away_team', 'Unknown'))
                else:
                    possession_team = game.get('home_team_abbr', 'Unknown')
            
            parts.append(f"🏈 **{possession_team}** has possession")
        
        if situation.get('downDistanceText'):
            parts.append(f"📏 {situation['downDistanceText']}")
        
        if situation.get('possessionText'):
            parts.append(f"📍 {situation['possessionText']}")
        
        return "\n".join(parts) if parts else ""
    elif league == 'mlb':
        parts = []
        if situation.get('batter'):
            batter_name = situation['batter'].get('athlete', {}).get('displayName', 'Unknown')
            parts.append(f"⚾ **At Bat:** {batter_name}")
        
        if situation.get('balls') is not None and situation.get('strikes') is not None:
            balls = situation.get('balls', 0)
            strikes = situation.get('strikes', 0)
            outs = situation.get('outs', 0)
            parts.append(f"**Count:** {balls}-{strikes}, {outs} out(s)")
        
        if situation.get('onFirst') or situation.get('onSecond') or situation.get('onThird'):
            bases = []
            if situation.get('onFirst'):
                bases.append('1st')
            if situation.get('onSecond'):
                bases.append('2nd')
            if situation.get('onThird'):
                bases.append('3rd')
            if bases:
                parts.append(f"🔶 Runners on: {', '.join(bases)}")
        
        return "\n".join(parts) if parts else ""
    
    return ""

def get_period_name(league: str, period: int) -> str:
    if league == 'nfl':
        if period <= 4:
            return f"Q{period}"
        else:
            return f"OT{period - 4}"
    elif league == 'nba':
        if period <= 4:
            return f"Q{period}"
        else:
            return f"OT{period - 4}"
    elif league == 'nhl':
        if period <= 3:
            return f"Period {period}"
        else:
            return "OT"
    elif league == 'mlb':
        return f"Inning {period}"
    return f"Period {period}"

class ScoreCommands(commands.Cog):
    def __init__(self, bot, sports_api, game_tracker):
        self.bot = bot
        self.sports_api = sports_api
        self.game_tracker = game_tracker
    
    @commands.command(name='scores')
    async def scores(self, ctx, league: str = None):
        if league and league.lower() not in ['nfl', 'mlb', 'nba', 'nhl']:
            await ctx.send("Please specify a valid league: NFL, MLB, NBA, or NHL")
            return
        
        leagues_to_check = [league.lower()] if league else ['nfl', 'mlb', 'nba', 'nhl']
        
        await ctx.send("🔍 Fetching scores from Blazed A.I Sports Network...")
        
        for lg in leagues_to_check:
            data = await self.sports_api.fetch_scores(lg)
            if not data:
                await ctx.send(f"⚠️ Could not fetch {lg.upper()} scores at this time.")
                continue
            
            games = self.sports_api.parse_games(data, lg)
            if not games:
                await ctx.send(f"📅 No {lg.upper()} games scheduled today.")
                continue
            
            for game in games:
                embed = create_game_embed(game, lg, self.bot.user)
                await ctx.send(embed=embed)
    
    @commands.command(name='track')
    async def track(self, ctx, league: str = None):
        if league and league.lower() not in ['nfl', 'mlb', 'nba', 'nhl']:
            await ctx.send("Please specify a valid league: NFL, MLB, NBA, or NHL")
            return
        
        leagues_to_track = [league.lower()] if league else ['nfl', 'mlb', 'nba', 'nhl']
        
        await ctx.send("🔴 Setting up live score tracking with Blazed A.I...")
        
        for lg in leagues_to_track:
            data = await self.sports_api.fetch_scores(lg)
            if not data:
                continue
            
            games = self.sports_api.parse_games(data, lg)
            active_games = [g for g in games if not g['completed']]
            
            if not active_games:
                await ctx.send(f"📅 No active {lg.upper()} games to track right now.")
                continue
            
            for game in active_games:
                embed = create_game_embed(game, lg, self.bot.user)
                message = await ctx.send(embed=embed)
                self.game_tracker.add_tracked_message(game['id'], message, lg)
                score_key = f"{game['away_score']}-{game['home_score']}"
                self.game_tracker.update_last_score(game['id'], score_key)
        
        tracked_count = len(self.game_tracker.get_tracked_games())
        await ctx.send(f"✅ Now tracking **{tracked_count}** active game(s)! Embeds will auto-update every 30 seconds.")
    
    @commands.command(name='stoptrack')
    async def stoptrack(self, ctx):
        count = len(self.game_tracker.get_tracked_games())
        self.game_tracker.tracked_messages.clear()
        await ctx.send(f"⏹️ Stopped tracking **{count}** game(s). Use `!track` to start tracking again.")
    
    @commands.command(name='help_sports')
    async def help_sports(self, ctx):
        embed = discord.Embed(
            title="⚡ Blazed A.I Sports Tracker",
            description="Real-time sports scores with auto-updating embeds",
            color=0xFF6B00
        )
        
        embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=self.bot.user.display_avatar.url
        )
        
        embed.add_field(
            name="📊 !scores [league]",
            value="Display current scores\n`!scores nfl` or `!scores` for all leagues",
            inline=False
        )
        
        embed.add_field(
            name="🔴 !track [league]",
            value="Track live games with auto-updating embeds\n`!track nba` or `!track` for all leagues",
            inline=False
        )
        
        embed.add_field(
            name="⏹️ !stoptrack",
            value="Stop tracking all games",
            inline=False
        )
        
        embed.add_field(
            name="🏈 Supported Leagues",
            value="NFL • MLB • NBA • NHL",
            inline=False
        )
        
        embed.set_footer(
            text="Blazed A.I • Powered by ESPN",
            icon_url=self.bot.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)

async def setup(bot, sports_api, game_tracker):
    await bot.add_cog(ScoreCommands(bot, sports_api, game_tracker))
