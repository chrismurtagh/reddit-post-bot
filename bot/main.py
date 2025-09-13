#!/usr/bin/env python3

import os
import sys
import logging
import schedule
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

from config_reader import ConfigReader
from reddit_client import RedditClient
from summary_generator import SummaryGenerator

def setup_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_environment():
    load_dotenv()

    required_vars = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USERNAME',
        'REDDIT_PASSWORD'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return {
        'client_id': os.getenv('REDDIT_CLIENT_ID'),
        'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
        'username': os.getenv('REDDIT_USERNAME'),
        'password': os.getenv('REDDIT_PASSWORD'),
        'user_agent': os.getenv('REDDIT_USER_AGENT', 'DayZServerBot/1.0')
    }

def run_posting_job():
    logger = logging.getLogger(__name__)
    logger.info("Starting daily posting job...")

    try:
        config_reader = ConfigReader()

        if not config_reader.validate_config():
            logger.error("Configuration validation failed, aborting posting job")
            return

        env_vars = load_environment()

        reddit_client = RedditClient(
            client_id=env_vars['client_id'],
            client_secret=env_vars['client_secret'],
            user_agent=env_vars['user_agent'],
            username=env_vars['username'],
            password=env_vars['password']
        )

        subreddits = config_reader.read_subreddits()
        post_content = config_reader.read_post_content()
        image_path = config_reader.get_post_image_path()

        logger.info(f"Posting to {len(subreddits)} subreddits...")
        logger.info(f"Title: {post_content['title'][:50]}...")
        logger.info(f"Image: {'Yes' if image_path else 'No'}")

        delay_between_posts = int(os.getenv('POST_DELAY_SECONDS', '30'))

        results = reddit_client.post_to_multiple_subreddits(
            subreddits=subreddits,
            title=post_content['title'],
            body=post_content['body'],
            image_path=image_path,
            flair=post_content['flair'] if post_content['flair'] else None,
            delay_between_posts=delay_between_posts
        )

        summary_generator = SummaryGenerator()

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        summary_generator.save_post_results(results, timestamp)

        logger.info("Waiting 5 minutes before generating summary to allow Reddit stats to update...")
        time.sleep(300)

        summary = summary_generator.generate_daily_summary(results, reddit_client)
        summary_generator.save_daily_summary(summary)
        summary_generator.save_text_summary(summary)

        text_summary = summary_generator.create_text_summary(summary)
        print("\n" + "="*60)
        print("DAILY POSTING SUMMARY")
        print("="*60)
        print(text_summary)

        successful_posts = len([r for r in results if r['success']])
        logger.info(f"Posting job completed: {successful_posts}/{len(results)} posts successful")

    except Exception as e:
        logger.error(f"Error in posting job: {e}", exc_info=True)

def main():
    try:
        setup_logging()
        logger = logging.getLogger(__name__)

        if len(sys.argv) > 1 and sys.argv[1] == '--run-once':
            logger.info("Running posting job once and exiting...")
            run_posting_job()
            return

        post_time = os.getenv('POST_TIME', '09:00')
        timezone_name = os.getenv('TIMEZONE', 'UTC')

        logger.info(f"Scheduling daily posts at {post_time} ({timezone_name})")

        schedule.every().day.at(post_time).do(run_posting_job)

        logger.info("Bot started. Waiting for scheduled time...")
        logger.info("Press Ctrl+C to stop")

        while True:
            schedule.run_pending()
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()