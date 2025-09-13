import praw
import time
import logging
from typing import List, Dict, Optional, Tuple
from PIL import Image
import os

logger = logging.getLogger(__name__)

class RedditClient:
    def __init__(self, client_id: str, client_secret: str, user_agent: str, username: str, password: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )

        try:
            self.reddit.user.me()
            logger.info(f"Successfully authenticated as {username}")
        except Exception as e:
            logger.error(f"Failed to authenticate with Reddit: {e}")
            raise

    def submit_post(self, subreddit_name: str, title: str, body: str, image_path: Optional[str] = None, flair: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            if image_path and os.path.exists(image_path):
                submission = subreddit.submit_image(
                    title=title,
                    image_path=image_path,
                    selftext=body,
                    flair_text=flair
                )
                logger.info(f"Image post submitted to r/{subreddit_name}: {submission.url}")
            else:
                submission = subreddit.submit(
                    title=title,
                    selftext=body,
                    flair_text=flair
                )
                logger.info(f"Text post submitted to r/{subreddit_name}: {submission.url}")

            return True, submission.url, submission.id

        except praw.exceptions.RedditAPIException as e:
            error_msg = f"Reddit API error posting to r/{subreddit_name}: {e}"
            logger.error(error_msg)
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Unexpected error posting to r/{subreddit_name}: {e}"
            logger.error(error_msg)
            return False, error_msg, None


    def validate_image(self, image_path: str) -> bool:
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return False

            file_size = os.path.getsize(image_path)
            max_size = 20 * 1024 * 1024
            if file_size > max_size:
                logger.error(f"Image file too large: {file_size} bytes (max: {max_size})")
                return False

            with Image.open(image_path) as img:
                width, height = img.size
                if width > 10000 or height > 10000:
                    logger.error(f"Image dimensions too large: {width}x{height}")
                    return False

            logger.info(f"Image validation passed: {image_path}")
            return True

        except Exception as e:
            logger.error(f"Error validating image {image_path}: {e}")
            return False

    def check_rate_limit(self) -> None:
        try:
            ratelimit_remaining = self.reddit.auth.limits.get('remaining', 0)
            ratelimit_used = self.reddit.auth.limits.get('used', 0)

            logger.info(f"Rate limit - Remaining: {ratelimit_remaining}, Used: {ratelimit_used}")

            if ratelimit_remaining < 10:
                logger.warning("Low rate limit remaining, adding delay")
                time.sleep(60)

        except Exception as e:
            logger.warning(f"Could not check rate limit: {e}")

    def post_to_multiple_subreddits(self, subreddits: List[str], title: str, body: str,
                                   image_path: Optional[str] = None, flair: Optional[str] = None,
                                   delay_between_posts: int = 30) -> List[Dict]:
        results = []

        if image_path and not self.validate_image(image_path):
            logger.error("Image validation failed, skipping image posts")
            image_path = None

        for i, subreddit in enumerate(subreddits):
            self.check_rate_limit()

            success, url_or_error, post_id = self.submit_post(
                subreddit_name=subreddit,
                title=title,
                body=body,
                image_path=image_path,
                flair=flair
            )

            result = {
                'subreddit': subreddit,
                'success': success,
                'url': url_or_error if success else None,
                'error': url_or_error if not success else None,
                'post_id': post_id,
                'timestamp': time.time()
            }

            results.append(result)

            if i < len(subreddits) - 1:
                logger.info(f"Waiting {delay_between_posts} seconds before next post...")
                time.sleep(delay_between_posts)

        return results