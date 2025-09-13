import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigReader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)

    def read_subreddits(self) -> List[str]:
        subreddits_file = self.config_dir / "subreddits.txt"
        try:
            with open(subreddits_file, 'r', encoding='utf-8') as f:
                subreddits = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            logger.info(f"Loaded {len(subreddits)} subreddits from {subreddits_file}")
            return subreddits
        except FileNotFoundError:
            logger.error(f"Subreddits file not found: {subreddits_file}")
            return []
        except Exception as e:
            logger.error(f"Error reading subreddits file: {e}")
            return []

    def read_post_content(self) -> Dict[str, str]:
        content_file = self.config_dir / "post_content.txt"
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            post_data = {
                'title': '',
                'body': '',
                'flair': ''
            }

            lines = content.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if line.startswith('[TITLE]'):
                    current_section = 'title'
                    continue
                elif line.startswith('[BODY]'):
                    current_section = 'body'
                    continue
                elif line.startswith('[FLAIR]'):
                    current_section = 'flair'
                    continue

                if current_section and line:
                    if post_data[current_section]:
                        post_data[current_section] += '\n' + line
                    else:
                        post_data[current_section] = line

            logger.info(f"Loaded post content from {content_file}")
            return post_data

        except FileNotFoundError:
            logger.error(f"Post content file not found: {content_file}")
            return {'title': '', 'body': '', 'flair': ''}
        except Exception as e:
            logger.error(f"Error reading post content file: {e}")
            return {'title': '', 'body': '', 'flair': ''}

    def get_post_image_path(self) -> Optional[str]:
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

        for ext in image_extensions:
            image_file = self.config_dir / f"post_image{ext}"
            if image_file.exists():
                logger.info(f"Found post image: {image_file}")
                return str(image_file)

        logger.info("No post image found")
        return None

    def validate_config(self) -> bool:
        subreddits = self.read_subreddits()
        post_content = self.read_post_content()

        if not subreddits:
            logger.error("No subreddits configured")
            return False

        if not post_content['title']:
            logger.error("No post title configured")
            return False

        if not post_content['body']:
            logger.error("No post body configured")
            return False

        logger.info("Configuration validation passed")
        return True