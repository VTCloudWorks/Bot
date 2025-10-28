# Discord Sports Score Bot

## Overview
A Discord bot that automatically displays and updates live game scores from NFL, MLB, NBA, and NHL. The bot uses Discord embeds that refresh in real-time whenever there's a score change.

## Features
- Real-time score tracking for NFL, MLB, NBA, and NHL games
- Auto-updating Discord embeds that refresh when scores change
- Rich embed display with team information, scores, game status, and period/quarter/inning
- Background polling task to detect score changes
- Commands to track specific games or all active games

## Project Structure
- `main.py` - Discord bot entry point and main logic
- `sports_api.py` - Sports data fetching from ESPN API
- `bot_commands.py` - Discord command handlers
- `config.py` - Configuration and constants
- `.env` - Environment variables (Discord token)

## Recent Changes
- 2025-10-28: Initial project setup with Python 3.11

## User Preferences
- Automatic embed updates on score changes
- Support for NFL, MLB, NBA, and NHL leagues
- Using API keys directly (not Discord connector)

## Dependencies
- discord.py - Discord bot framework
- aiohttp - Async HTTP requests
- python-dotenv - Environment variable management
