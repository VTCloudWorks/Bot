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
    
    status_emoji = "🔴" if not game['completed'] and game['period'] > 0 else ("✅" if game['completed'] else "⏰")
    title = f"{status_emoji} {game['away_team_abbr']} @ {game['home_team_abbr']}"
    
    embed = discord.Embed(
        title=title,
        color=color
    )
    
    if bot_user:
        embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=bot_user.display_avatar.url
        )
    
    away_abbr = game['away_team_abbr'] or game['away_team'][:3].upper()
    home_abbr = game['home_team_abbr'] or game['home_team'][:3].upper()
    score_text = f"**{away_abbr}** {game['away_score']} - {game['home_score']} **{home_abbr}**"
    embed.add_field(name="Score", value=score_text, inline=True)
    
    status_text = game['detail']
    if game['period'] > 0 and not game['completed'] and game['clock']:
        period_name = get_period_name(league, game['period'])
        status_text = f"{period_name} - {game['clock']}"
    embed.add_field(name="Status", value=status_text, inline=True)
    
    if game['home_record'] or game['away_record']:
        records = f"{game['away_record']} / {game['home_record']}"
        embed.add_field(name="Records", value=records, inline=True)
    
    footer_text = f"Blazed A.I • {league_name}"
    embed.set_footer(
        text=footer_text,
        icon_url=bot_user.display_avatar.url if bot_user else None
    )
    
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
            error_embed = discord.Embed(
                description="⚠️ Please specify a valid league: NFL, MLB, NBA, or NHL",
                color=0xFF0000
            )
            error_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            error_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=error_embed)
            return
        
        leagues_to_check = [league.lower()] if league else ['nfl', 'mlb', 'nba', 'nhl']
        
        fetch_embed = discord.Embed(
            description="🔍 Fetching scores...",
            color=0xFF6B00
        )
        fetch_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=self.bot.user.display_avatar.url
        )
        fetch_embed.set_footer(
            text="Blazed A.I",
            icon_url=self.bot.user.display_avatar.url
        )
        await ctx.send(embed=fetch_embed)
        
        for lg in leagues_to_check:
            data = await self.sports_api.fetch_scores(lg)
            if not data:
                error_embed = discord.Embed(
                    description=f"⚠️ Could not fetch {lg.upper()} scores at this time.",
                    color=0xFF0000
                )
                error_embed.set_author(
                    name="Blazed A.I Sports Tracker",
                    icon_url=self.bot.user.display_avatar.url
                )
                error_embed.set_footer(
                    text="Blazed A.I",
                    icon_url=self.bot.user.display_avatar.url
                )
                await ctx.send(embed=error_embed)
                continue
            
            games = self.sports_api.parse_games(data, lg)
            if not games:
                info_embed = discord.Embed(
                    description=f"📅 No {lg.upper()} games scheduled today.",
                    color=0xFFA500
                )
                info_embed.set_author(
                    name="Blazed A.I Sports Tracker",
                    icon_url=self.bot.user.display_avatar.url
                )
                info_embed.set_footer(
                    text="Blazed A.I",
                    icon_url=self.bot.user.display_avatar.url
                )
                await ctx.send(embed=info_embed)
                continue
            
            for game in games:
                embed = create_game_embed(game, lg, self.bot.user)
                await ctx.send(embed=embed)
    
    @commands.command(name='track')
    async def track(self, ctx, league: str = None):
        if league and league.lower() not in ['nfl', 'mlb', 'nba', 'nhl']:
            error_embed = discord.Embed(
                description="⚠️ Please specify a valid league: NFL, MLB, NBA, or NHL",
                color=0xFF0000
            )
            error_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            error_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=error_embed)
            return
        
        leagues_to_track = [league.lower()] if league else ['nfl', 'mlb', 'nba', 'nhl']
        
        setup_embed = discord.Embed(
            description="🔴 Setting up live score tracking...",
            color=0xFF6B00
        )
        setup_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=self.bot.user.display_avatar.url
        )
        setup_embed.set_footer(
            text="Blazed A.I",
            icon_url=self.bot.user.display_avatar.url
        )
        await ctx.send(embed=setup_embed)
        
        for lg in leagues_to_track:
            data = await self.sports_api.fetch_scores(lg)
            if not data:
                continue
            
            games = self.sports_api.parse_games(data, lg)
            active_games = [g for g in games if not g['completed']]
            
            if not active_games:
                info_embed = discord.Embed(
                    description=f"📅 No active {lg.upper()} games to track right now.",
                    color=0xFFA500
                )
                info_embed.set_author(
                    name="Blazed A.I Sports Tracker",
                    icon_url=self.bot.user.display_avatar.url
                )
                info_embed.set_footer(
                    text="Blazed A.I",
                    icon_url=self.bot.user.display_avatar.url
                )
                await ctx.send(embed=info_embed)
                continue
            
            for game in active_games:
                embed = create_game_embed(game, lg, self.bot.user)
                message = await ctx.send(embed=embed)
                self.game_tracker.add_tracked_message(game['id'], message, lg)
                score_key = f"{game['away_score']}-{game['home_score']}"
                self.game_tracker.update_last_score(game['id'], score_key)
        
        tracked_count = len(self.game_tracker.get_tracked_games())
        success_embed = discord.Embed(
            description=f"✅ Now tracking **{tracked_count}** active game(s)! Embeds will auto-update every 30 seconds.",
            color=0x00FF00
        )
        success_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=self.bot.user.display_avatar.url
        )
        success_embed.set_footer(
            text="Blazed A.I",
            icon_url=self.bot.user.display_avatar.url
        )
        await ctx.send(embed=success_embed)
    
    @commands.command(name='stoptrack')
    async def stoptrack(self, ctx):
        count = len(self.game_tracker.get_tracked_games())
        self.game_tracker.tracked_messages.clear()
        stop_embed = discord.Embed(
            description=f"⏹️ Stopped tracking **{count}** game(s). Use `!track` to start tracking again.",
            color=0xFF0000
        )
        stop_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=self.bot.user.display_avatar.url
        )
        stop_embed.set_footer(
            text="Blazed A.I",
            icon_url=self.bot.user.display_avatar.url
        )
        await ctx.send(embed=stop_embed)
    
    @commands.command(name='games')
    async def games(self, ctx, league: str = None):
        if league and league.lower() not in ['nfl', 'mlb', 'nba', 'nhl']:
            error_embed = discord.Embed(
                description="⚠️ Please specify a valid league: NFL, MLB, NBA, or NHL",
                color=0xFF0000
            )
            error_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            error_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=error_embed)
            return
        
        leagues_to_check = [league.lower()] if league else ['nfl', 'mlb', 'nba', 'nhl']
        
        fetch_embed = discord.Embed(
            description="🔍 Fetching available games...",
            color=0xFF6B00
        )
        fetch_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=self.bot.user.display_avatar.url
        )
        fetch_embed.set_footer(
            text="Blazed A.I",
            icon_url=self.bot.user.display_avatar.url
        )
        await ctx.send(embed=fetch_embed)
        
        for lg in leagues_to_check:
            data = await self.sports_api.fetch_scores(lg)
            if not data:
                continue
            
            games = self.sports_api.parse_games(data, lg)
            if not games:
                continue
            
            embed = discord.Embed(
                title=f"{LEAGUE_NAMES.get(lg, lg.upper())} Games",
                color=LEAGUE_COLORS.get(lg, 0x000000)
            )
            
            embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            
            game_list = []
            for i, game in enumerate(games, 1):
                status = "🔴 Live" if not game['completed'] and game['period'] > 0 else ("✅ Final" if game['completed'] else "⏰ Scheduled")
                game_list.append(f"`{i}.` {game['away_team_abbr']} @ {game['home_team_abbr']} - {status}")
            
            if game_list:
                embed.add_field(name="Available Games", value="\n".join(game_list), inline=False)
                embed.add_field(name="How to Track", value=f"Use `!trackgame {lg} <number>` to track a specific game\nExample: `!trackgame {lg} 1`", inline=False)
                embed.set_footer(
                    text=f"Blazed A.I • {LEAGUE_NAMES.get(lg, lg.upper())}",
                    icon_url=self.bot.user.display_avatar.url
                )
                await ctx.send(embed=embed)
    
    @commands.command(name='trackgame')
    async def trackgame(self, ctx, league: str = None, game_number: int = None):
        if not league or not game_number:
            usage_embed = discord.Embed(
                title="Track Game Usage",
                description="Usage: `!trackgame <league> <game_number>`\nExample: `!trackgame nfl 1`\nUse `!games` to see available games.",
                color=0xFFA500
            )
            usage_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            usage_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=usage_embed)
            return
        
        if league.lower() not in ['nfl', 'mlb', 'nba', 'nhl']:
            error_embed = discord.Embed(
                description="⚠️ Please specify a valid league: NFL, MLB, NBA, or NHL",
                color=0xFF0000
            )
            error_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            error_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=error_embed)
            return
        
        lg = league.lower()
        data = await self.sports_api.fetch_scores(lg)
        if not data:
            error_embed = discord.Embed(
                description=f"⚠️ Could not fetch {lg.upper()} games at this time.",
                color=0xFF0000
            )
            error_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            error_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=error_embed)
            return
        
        games = self.sports_api.parse_games(data, lg)
        if not games or game_number < 1 or game_number > len(games):
            error_embed = discord.Embed(
                description=f"❌ Invalid game number. Use `!games {lg}` to see available games.",
                color=0xFF0000
            )
            error_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            error_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=error_embed)
            return
        
        game = games[game_number - 1]
        
        if game['completed']:
            error_embed = discord.Embed(
                description="⚠️ This game has already completed. Only active games can be tracked.",
                color=0xFF0000
            )
            error_embed.set_author(
                name="Blazed A.I Sports Tracker",
                icon_url=self.bot.user.display_avatar.url
            )
            error_embed.set_footer(
                text="Blazed A.I",
                icon_url=self.bot.user.display_avatar.url
            )
            await ctx.send(embed=error_embed)
            return
        
        embed = create_game_embed(game, lg, self.bot.user)
        message = await ctx.send(embed=embed)
        self.game_tracker.add_tracked_message(game['id'], message, lg)
        score_key = f"{game['away_score']}-{game['home_score']}"
        self.game_tracker.update_last_score(game['id'], score_key)
        
        success_embed = discord.Embed(
            description=f"✅ Now tracking {game['away_team_abbr']} @ {game['home_team_abbr']}! Embed will auto-update every 30 seconds.",
            color=0x00FF00
        )
        success_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=self.bot.user.display_avatar.url
        )
        success_embed.set_footer(
            text="Blazed A.I",
            icon_url=self.bot.user.display_avatar.url
        )
        await ctx.send(embed=success_embed)
    
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
            name="🎯 !games [league]",
            value="List available games with numbers\n`!games nfl` to see game options",
            inline=False
        )
        
        embed.add_field(
            name="🔴 !track [league]",
            value="Track all live games in a league\n`!track nba` or `!track` for all leagues",
            inline=False
        )
        
        embed.add_field(
            name="🎮 !trackgame <league> <number>",
            value="Track a specific game\n`!trackgame nfl 1` to track game #1",
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
            text="Blazed A.I",
            icon_url=self.bot.user.display_avatar.url
        )
        
        await ctx.send(embed=embed)

async def setup(bot, sports_api, game_tracker):
    await bot.add_cog(ScoreCommands(bot, sports_api, game_tracker))
