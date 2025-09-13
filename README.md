# Reddit DayZ Server Bot 🎮

An automated Reddit posting bot specifically designed for DayZ server advertising. This bot supports both text and image posts with simple, clean logging.

## Features

- 🚀 **Automated Posting**: Schedule daily posts to multiple subreddits
- 🖼️ **Image Support**: Post screenshots with text descriptions
- 🔄 **Rate Limiting**: Respects Reddit's API limits
- 📝 **Simple Logging**: Clean console output and basic log files
- 🐳 **Docker Ready**: Easy deployment with Docker Compose
- ⏰ **Flexible Scheduling**: Configurable posting times and timezones

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd reddit-post
cp .env.example .env
```

### 2. Configure Reddit API

1. Go to https://www.reddit.com/prefs/apps/
2. Create a new "script" application
3. Edit `.env` with your Reddit credentials:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### 3. Configure Your Posts

Edit `config/post_content.txt`:
```
[TITLE]
🎮 [US/EU] Your DayZ Server | PvP/PvE | High Pop!

[BODY]
Your server description here...

[FLAIR]
Server Advertisement
```

Edit `config/subreddits.txt`:
```
dayz
DayZServers
dayzlfg
```

### 4. Add Server Image (Optional)

Place your server screenshot as `config/post_image.jpg` (or .png, .gif)

### 5. Run the Bot

**With Docker (Recommended):**
```bash
# Test run (posts once and exits)
docker-compose --profile test up reddit-bot-test

# Production run (daily scheduled posts)
docker-compose up -d reddit-bot
```

**Without Docker:**
```bash
pip install -r requirements.txt
cd bot
python main.py --run-once  # Test run
python main.py             # Scheduled run
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POST_TIME` | Daily posting time (24h format) | `09:00` |
| `TIMEZONE` | Timezone for scheduling | `UTC` |
| `POST_DELAY_SECONDS` | Delay between subreddit posts | `30` |

### Configuration Files

**`config/subreddits.txt`**: List of target subreddits (one per line)
**`config/post_content.txt`**: Post title, body, and flair
**`config/post_image.jpg`**: Optional server image

## Project Structure

```
reddit-post/
├── bot/
│   ├── main.py              # Main bot application
│   ├── reddit_client.py     # Reddit API wrapper
│   └── config_reader.py     # Configuration parser
├── config/
│   ├── subreddits.txt       # Target subreddits
│   ├── post_content.txt     # Post content
│   └── post_image.jpg       # Optional image
├── logs/                    # Basic log files
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Logging

The bot provides simple, clean logging:

- **Console Output**: Real-time status updates during posting
- **Log File**: Basic application logs saved to `logs/bot.log`
- **Success/Failure**: Clear indication of which posts succeeded or failed

### Example Output

```
2024-01-15 09:00:01 - INFO - Starting daily posting job...
2024-01-15 09:00:02 - INFO - Posting to 3 subreddits...
2024-01-15 09:00:03 - INFO - ✅ Posted to r/dayz: https://reddit.com/r/dayz/comments/abc123
2024-01-15 09:00:33 - INFO - ✅ Posted to r/DayZServers: https://reddit.com/r/DayZServers/comments/def456
2024-01-15 09:01:03 - ERROR - ❌ Failed to post to r/dayzlfg: Subreddit not found
2024-01-15 09:01:03 - INFO - Posting completed: 2 successful, 1 failed
```

## Docker Commands

```bash
# Build and start scheduled bot
docker-compose up -d reddit-bot

# Test run (posts once)
docker-compose --profile test up reddit-bot-test

# View logs
docker-compose logs -f reddit-bot

# Stop bot
docker-compose down

# Rebuild after changes
docker-compose build reddit-bot
```

## Reddit API Guidelines

- **Rate Limits**: The bot respects Reddit's 1 post per 10 minutes limit
- **Content Policy**: Ensure your posts comply with subreddit rules
- **Account Requirements**: Use an account with sufficient karma and age
- **Best Practices**: Vary your content and engage with the community

## Troubleshooting

### Common Issues

**Authentication Failed**:
- Verify Reddit API credentials in `.env`
- Ensure account has sufficient karma/age

**Posts Rejected**:
- Check subreddit rules and required flairs
- Verify image size (max 20MB) and format

**Scheduling Issues**:
- Confirm timezone settings
- Check Docker container logs

### Debug Mode

Run with verbose logging:
```bash
# Local debugging
cd bot
python main.py --run-once

# Docker debugging
docker-compose logs reddit-bot
```

## License

This project is for educational and legitimate server advertising purposes only. Ensure compliance with Reddit's Terms of Service and individual subreddit rules.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the console output and `logs/bot.log`
2. Review Reddit API documentation
3. Verify subreddit posting rules
4. Open an issue with detailed logs and error messages