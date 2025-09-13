import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SummaryGenerator:
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

    def save_post_results(self, results: List[Dict], timestamp: Optional[str] = None) -> str:
        if not timestamp:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        filename = f"post_results_{timestamp}.json"
        filepath = self.logs_dir / filename

        post_data = {
            'timestamp': timestamp,
            'run_date': datetime.now(timezone.utc).isoformat(),
            'total_posts_attempted': len(results),
            'successful_posts': len([r for r in results if r['success']]),
            'failed_posts': len([r for r in results if not r['success']]),
            'results': results
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, default=str)

            logger.info(f"Post results saved to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error saving post results: {e}")
            return ""

    def generate_daily_summary(self, results: List[Dict], reddit_client=None) -> Dict:
        successful_posts = [r for r in results if r['success']]
        failed_posts = [r for r in results if not r['success']]

        summary = {
            'date': datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            'total_posts_attempted': len(results),
            'successful_posts': len(successful_posts),
            'failed_posts': len(failed_posts),
            'success_rate': round(len(successful_posts) / len(results) * 100, 1) if results else 0,
            'posts': []
        }

        for result in results:
            post_info = {
                'subreddit': result['subreddit'],
                'success': result['success'],
                'url': result.get('url'),
                'error': result.get('error'),
                'timestamp': result.get('timestamp'),
                'stats': None
            }

            if result['success'] and result.get('post_id') and reddit_client:
                try:
                    stats = reddit_client.get_post_stats(result['post_id'])
                    post_info['stats'] = stats
                except Exception as e:
                    logger.warning(f"Could not fetch stats for post {result['post_id']}: {e}")

            summary['posts'].append(post_info)

        total_engagement = self._calculate_total_engagement(summary['posts'])
        summary.update(total_engagement)

        return summary

    def _calculate_total_engagement(self, posts: List[Dict]) -> Dict:
        total_upvotes = 0
        total_comments = 0
        total_score = 0
        posts_with_stats = 0

        for post in posts:
            if post.get('stats'):
                total_upvotes += post['stats'].get('upvotes', 0)
                total_comments += post['stats'].get('comments', 0)
                total_score += post['stats'].get('score', 0)
                posts_with_stats += 1

        return {
            'total_upvotes': total_upvotes,
            'total_comments': total_comments,
            'total_score': total_score,
            'average_score': round(total_score / posts_with_stats, 1) if posts_with_stats else 0,
            'average_upvotes': round(total_upvotes / posts_with_stats, 1) if posts_with_stats else 0
        }

    def save_daily_summary(self, summary: Dict, date: Optional[str] = None) -> str:
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y%m%d")

        filename = f"daily_summary_{date}.json"
        filepath = self.logs_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"Daily summary saved to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error saving daily summary: {e}")
            return ""

    def create_text_summary(self, summary: Dict) -> str:
        text_summary = f"""
Reddit Bot Daily Summary - {summary['date']}
{'=' * 50}

POSTING OVERVIEW:
• Total posts attempted: {summary['total_posts_attempted']}
• Successful posts: {summary['successful_posts']}
• Failed posts: {summary['failed_posts']}
• Success rate: {summary['success_rate']}%

ENGAGEMENT METRICS:
• Total upvotes: {summary.get('total_upvotes', 'N/A')}
• Total comments: {summary.get('total_comments', 'N/A')}
• Total score: {summary.get('total_score', 'N/A')}
• Average score per post: {summary.get('average_score', 'N/A')}
• Average upvotes per post: {summary.get('average_upvotes', 'N/A')}

POST DETAILS:
"""

        for post in summary['posts']:
            status = "✅ SUCCESS" if post['success'] else "❌ FAILED"
            text_summary += f"\n{status} - r/{post['subreddit']}\n"

            if post['success']:
                text_summary += f"  URL: {post['url']}\n"
                if post.get('stats'):
                    stats = post['stats']
                    text_summary += f"  Stats: {stats['score']} score, {stats['upvotes']} upvotes, {stats['comments']} comments ({stats['upvote_ratio']}% upvoted)\n"
            else:
                text_summary += f"  Error: {post['error']}\n"

        if summary['failed_posts'] > 0:
            text_summary += f"\nFAILED POSTS SUMMARY:\n"
            failed_subreddits = [p['subreddit'] for p in summary['posts'] if not p['success']]
            text_summary += f"Failed subreddits: {', '.join(failed_subreddits)}\n"

        return text_summary

    def save_text_summary(self, summary: Dict, date: Optional[str] = None) -> str:
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y%m%d")

        filename = f"daily_summary_{date}.txt"
        filepath = self.logs_dir / filename

        text_content = self.create_text_summary(summary)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_content)

            logger.info(f"Text summary saved to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error saving text summary: {e}")
            return ""

    def get_historical_summaries(self, days: int = 7) -> List[Dict]:
        summary_files = list(self.logs_dir.glob("daily_summary_*.json"))
        summary_files.sort(key=lambda x: x.name, reverse=True)

        summaries = []
        for filepath in summary_files[:days]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                    summaries.append(summary)
            except Exception as e:
                logger.warning(f"Could not load summary from {filepath}: {e}")

        return summaries