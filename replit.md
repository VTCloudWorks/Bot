# Discord Sports Score Bot

## Overview

A Discord bot that provides real-time sports score tracking for NFL, MLB, NBA, and NHL games. The bot fetches live game data from ESPN's public API and displays it in auto-updating Discord embeds. When scores change, the bot automatically refreshes the embed without creating new messages, providing a seamless live-score experience for Discord server members.

## User Preferences

- Preferred communication style: Simple, everyday language
- Embed design: Compact, horizontal layout with minimal branding
- Footer: Show only league name, no timestamp or extra branding

## System Architecture

### Application Type
- **Discord Bot Application**: Event-driven bot built with discord.py that responds to commands and maintains background polling tasks

### Core Components

**Bot Framework (main.py)**
- Uses discord.py with command extensions for structured command handling
- Implements privileged intents (message_content) to read user commands
- Runs a background task loop that polls for score updates every 30 seconds
- Manages bot lifecycle including startup, command registration, and the auto-update task

**Sports Data Layer (sports_api.py)**
- Encapsulates all ESPN API interactions in a dedicated `SportsAPI` class
- Uses aiohttp for async HTTP requests to avoid blocking Discord event loop
- Maintains a persistent session for efficient connection reuse
- Parses ESPN's JSON response into normalized game dictionaries
- Supports four leagues (NFL, MLB, NBA, NHL) via separate API endpoints

**Command Handler (bot_commands.py)**
- Defines a `GameTracker` class to maintain state of actively tracked games
- Tracks which Discord messages are displaying which games
- Stores last known scores to detect changes and trigger updates
- Creates compact Discord embeds with horizontal layout, team abbreviations, scores, status, and records
- Embeds use inline fields for a professional, space-efficient presentation

**Configuration (config.py)**
- Centralizes all configuration including API URLs, league colors, and update intervals
- Loads Discord bot token from environment variables via python-dotenv
- Defines league-specific metadata (colors, display names)

### Key Architectural Decisions

**Real-time Updates via Message Editing**
- **Problem**: Need to show live scores without spamming new messages
- **Solution**: Store references to Discord messages and edit them in-place when scores change
- **Rationale**: Provides clean UI experience and avoids message clutter; Discord API supports message editing

**Background Polling Pattern**
- **Problem**: Need continuous score updates without blocking command handling
- **Solution**: discord.py's `@tasks.loop` decorator runs async polling every 30 seconds
- **Rationale**: ESPN doesn't provide webhooks, so polling is necessary; 30-second interval balances freshness with API rate limits

**Stateful Game Tracking**
- **Problem**: Need to remember which games users are tracking across update cycles
- **Solution**: In-memory `GameTracker` dictionary mapping game IDs to message objects and metadata
- **Rationale**: Simple state management for a single-instance bot; avoids database overhead for ephemeral tracking data

**Async HTTP with Session Reuse**
- **Problem**: Many HTTP requests could slow down the bot
- **Solution**: Single aiohttp ClientSession shared across all API calls
- **Rationale**: Connection pooling improves performance; async prevents blocking Discord operations

**League-Agnostic Data Model**
- **Problem**: Different sports have different data structures
- **Solution**: Normalize all leagues into common game dictionary format during parsing
- **Rationale**: Simplifies command logic and embed generation; ESPN API structure is similar enough across leagues

### Data Flow

1. User issues `!scores [league]` command
2. Bot fetches current games from ESPN API for specified league(s)
3. Bot creates Discord embed(s) and sends to channel
4. Bot stores message reference in GameTracker
5. Background task polls ESPN API every 30 seconds
6. On score change detection, bot edits the stored message with updated embed
7. Process continues until game completes or tracking is stopped

## External Dependencies

**Discord API (via discord.py)**
- Purpose: Core bot framework and Discord platform integration
- Key features used: Commands extension, message embeds, message editing, background tasks
- Requires: Bot token from Discord Developer Portal, message content intent enabled

**ESPN Public API**
- Purpose: Source of live sports scores and game data
- Endpoints: Separate scoreboard APIs for NFL, MLB, NBA, NHL
- Format: JSON responses with game events, competitors, scores, and status
- No authentication required (public API)

**Python Libraries**
- `discord.py`: Discord bot framework with async support
- `aiohttp`: Async HTTP client for API requests
- `python-dotenv`: Environment variable management for bot token

**Environment Variables**
- `DISCORD_BOT_TOKEN`: Required Discord bot authentication token
- Stored in Replit Secrets for secure access

## Recent Changes

**2025-10-28: Initial Replit Setup**
- Installed Python 3.11 and dependencies (discord.py, aiohttp, python-dotenv)
- Set up workflow to run bot with `python main.py`
- Added .gitignore for Python projects

**2025-10-28: Embed Redesign**
- Redesigned embeds to be more compact and professional
- Changed layout from vertical to horizontal using inline fields
- Removed timestamp from footer (now shows only league name)
- Simplified embed to show: Score, Status, and Records in horizontal layout
- Removed excessive branding and reduced overall embed size significantly

**2025-10-28: Game Selection Features**
- Added `!games` command to list all available games with numbered selections
- Added `!trackgame <league> <number>` command to track specific individual games
- Removed all external references (ESPN URLs and branding)
- Removed all timestamps from embeds for cleaner presentation
- Users can now choose exactly which games to track instead of tracking all league games

**2025-10-28: Blazed A.I Branding Implementation**
- All bot responses now use branded embeds with "Blazed A.I Sports Tracker" author
- Bot logo appears in footer of every embed
- Footer text shows "Blazed A.I" branding throughout
- Maintained timestamp-free design as requested
- All error messages, info messages, and success messages use branded embeds
- Auto-update loop maintains branding when refreshing tracked games