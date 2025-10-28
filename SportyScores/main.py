import discord
from discord.ext import commands, tasks
import asyncio
from config import DISCORD_TOKEN, UPDATE_INTERVAL
from sports_api import SportsAPI
from bot_commands import GameTracker, setup as setup_commands, create_game_embed

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
sports_api = SportsAPI()
game_tracker = GameTracker()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    await setup_commands(bot, sports_api, game_tracker)
    
    if not update_scores.is_running():
        update_scores.start()
    
    print('Auto-update task started!')

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_scores():
    tracked_games = game_tracker.get_tracked_games()
    
    if not tracked_games:
        return
    
    games_to_remove = []
    
    for game_id, tracked_info in tracked_games.items():
        league = tracked_info['league']
        message = tracked_info['message']
        last_score = tracked_info['last_score']
        
        try:
            data = await sports_api.fetch_scores(league)
            if not data:
                continue
            
            games = sports_api.parse_games(data, league)
            current_game = next((g for g in games if g['id'] == game_id), None)
            
            if not current_game:
                continue
            
            current_score = f"{current_game['away_score']}-{current_game['home_score']}"
            
            if current_game['completed']:
                embed = create_game_embed(current_game, league, bot.user)
                await message.edit(embed=embed)
                games_to_remove.append(game_id)
                print(f"Game {game_id} completed and removed from tracking")
            elif current_score != last_score:
                embed = create_game_embed(current_game, league, bot.user)
                await message.edit(embed=embed)
                game_tracker.update_last_score(game_id, current_score)
                print(f"Updated score for game {game_id}: {current_score}")
        
        except discord.errors.NotFound:
            games_to_remove.append(game_id)
            print(f"Message for game {game_id} not found, removing from tracking")
        except Exception as e:
            print(f"Error updating game {game_id}: {e}")
    
    for game_id in games_to_remove:
        game_tracker.remove_tracked_message(game_id)

@update_scores.before_loop
async def before_update_scores():
    await bot.wait_until_ready()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        error_embed = discord.Embed(
            description="❌ Command not found. Use `!help_sports` for available commands.",
            color=0xFF0000
        )
        error_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=bot.user.display_avatar.url
        )
        error_embed.set_footer(
            text="Blazed A.I",
            icon_url=bot.user.display_avatar.url
        )
        await ctx.send(embed=error_embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        error_embed = discord.Embed(
            description=f"⚠️ Missing argument: {error.param}",
            color=0xFF0000
        )
        error_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=bot.user.display_avatar.url
        )
        error_embed.set_footer(
            text="Blazed A.I",
            icon_url=bot.user.display_avatar.url
        )
        await ctx.send(embed=error_embed)
    else:
        error_embed = discord.Embed(
            description=f"❌ An error occurred: {str(error)}",
            color=0xFF0000
        )
        error_embed.set_author(
            name="Blazed A.I Sports Tracker",
            icon_url=bot.user.display_avatar.url
        )
        error_embed.set_footer(
            text="Blazed A.I",
            icon_url=bot.user.display_avatar.url
        )
        await ctx.send(embed=error_embed)
        print(f"Error: {error}")

async def main():
    async with bot:
        try:
            await bot.start(DISCORD_TOKEN)
        finally:
            await sports_api.close_session()

if __name__ == '__main__':
    asyncio.run(main())
