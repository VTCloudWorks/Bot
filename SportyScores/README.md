# Discord Sports Score Bot

A Discord bot that automatically displays and updates live game scores from NFL, MLB, NBA, and NHL. The bot uses Discord embeds that refresh in real-time whenever there's a score change.

## Features

- **Real-time Score Updates**: Automatically updates Discord embeds when scores change
- **Multi-League Support**: NFL, MLB, NBA, and NHL
- **Rich Embeds**: Beautiful, color-coded embeds with team info, scores, game status, and records
- **Live Tracking**: Track multiple games simultaneously with auto-updates every 30 seconds
- **Easy Commands**: Simple command interface for viewing and tracking games

## Setup Instructions

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
5. Copy your bot token (you'll need this in step 3)

### 2. Invite Bot to Your Server

1. In the Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Embed Links`, `Read Message History`
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 3. Configure Environment Variables

1. Create a `.env` file in the project root
2. Add your Discord bot token:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```

### 4. Run the Bot

The bot will start automatically when you run this Repl. You can also run it manually:

```bash
python main.py
```

## Commands

- `!scores [league]` - Display current scores for all leagues or a specific league
  - Example: `!scores nfl` or `!scores` for all leagues

- `!track [league]` - Start tracking live games with auto-updating embeds
  - Example: `!track nba` or `!track` for all active games

- `!stoptrack` - Stop tracking all games

- `!help_sports` - Show help message with all commands

## Supported Leagues

- **NFL** - National Football League
- **MLB** - Major League Baseball
- **NBA** - National Basketball Association
- **NHL** - National Hockey League

## How It Works

1. The bot fetches live game data from ESPN's public API
2. When you use `!track`, the bot posts game embeds and stores their message IDs
3. A background task runs every 30 seconds checking for score changes
4. When a score changes, the bot automatically updates the embed
5. Completed games are removed from tracking automatically

## Technical Details

- **Language**: Python 3.11
- **Framework**: discord.py 2.6.4
- **API Source**: ESPN Public API
- **Update Interval**: 30 seconds
- **Dependencies**: discord.py, aiohttp, python-dotenv

## Troubleshooting

**Bot doesn't respond to commands:**
- Make sure Message Content Intent is enabled in Discord Developer Portal
- Check that the bot has proper permissions in your server
- Verify your bot token is correct in the `.env` file

**Scores not updating:**
- ESPN API might be temporarily unavailable
- Check the console logs for error messages
- Ensure your internet connection is stable

**Bot disconnects frequently:**
- Check your Repl's always-on status
- Verify your Discord token hasn't expired

## Support

For issues or questions, check the console logs for detailed error messages.
