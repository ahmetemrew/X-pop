"""
Main Bot Orchestrator
"""

import os
import yaml
import logging
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

from .twitter_client import TwitterClient
from .ai_generator import AIGenerator
from .database import Database
from .duplicate_detector import DuplicateDetector


class XPopBot:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the X-Pop Bot"""
        # Load environment variables
        load_dotenv()

        # Setup logging
        self._setup_logging()

        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.logger.info("🚀 Initializing X-Pop Bot...")

        # Initialize components
        self.db = Database()
        self.duplicate_detector = DuplicateDetector(
            threshold=self.config['duplicate_detection']['similarity_threshold']
        )

        # Initialize Twitter client
        self.twitter = self._init_twitter_client()

        # Initialize AI generator
        self.ai = self._init_ai_generator()

        # Set personality
        personality = self.config['bot']['personality']
        self.ai.set_personality(personality)

        self.logger.info(f"✅ Bot initialized with personality: {personality}")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('logs/bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _init_twitter_client(self) -> TwitterClient:
        """Initialize Twitter API client"""
        try:
            return TwitterClient(
                api_key=os.getenv('TWITTER_API_KEY'),
                api_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {e}")
            raise

    def _init_ai_generator(self) -> AIGenerator:
        """Initialize AI generator"""
        try:
            return AIGenerator(
                api_key=os.getenv('GROQ_API_KEY'),
                model=self.config['ai']['model'],
                temperature=self.config['ai']['temperature'],
                max_tokens=self.config['ai']['max_tokens']
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize AI generator: {e}")
            raise

    def run_cycle(self):
        """Run one complete bot cycle"""
        self.logger.info("=" * 60)
        self.logger.info(f"🔄 Starting bot cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)

        try:
            # Step 1: Collect tweets
            collected_tweets = self.collect_tweets()

            if not collected_tweets:
                self.logger.info("📭 No new tweets collected")
                self._print_statistics()
                return

            # Step 2: Process and filter tweets
            processed_tweets = self.process_collected_tweets(collected_tweets)

            if not processed_tweets:
                self.logger.info("⚠️  No tweets to process after filtering")
                self._print_statistics()
                return

            # Step 3: Generate and post new tweets
            self.generate_and_post_tweets(processed_tweets)

            # Step 4: Print statistics
            self._print_statistics()

            self.logger.info("✅ Cycle completed successfully")

        except Exception as e:
            self.logger.error(f"❌ Error in bot cycle: {e}", exc_info=True)

    def collect_tweets(self) -> List[Dict]:
        """Collect tweets from monitored accounts"""
        self.logger.info("📡 Collecting tweets from monitored accounts...")

        accounts = self.config['monitored_accounts']
        max_per_user = self.config['bot']['max_tweets_per_run']

        all_tweets = self.twitter.get_tweets_from_multiple_users(
            accounts,
            max_per_user=max_per_user
        )

        # Filter by language (Turkish)
        all_tweets = self.twitter.filter_tweets_by_language(all_tweets, 'tr')

        # Filter by minimum length
        min_length = self.config['bot']['min_tweet_length']
        all_tweets = [t for t in all_tweets if len(t['text']) >= min_length]

        self.logger.info(f"📥 Collected {len(all_tweets)} tweets")

        # Store in database
        new_count = 0
        for tweet in all_tweets:
            if self.db.add_collected_tweet(
                tweet_id=str(tweet['id']),
                author=tweet['author'],
                content=tweet['text'],
                url=tweet['url']
            ):
                new_count += 1

        self.logger.info(f"💾 Stored {new_count} new tweets in database")

        return all_tweets

    def process_collected_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """Process and filter collected tweets"""
        self.logger.info("🔍 Processing collected tweets...")

        # Remove duplicates within the batch
        unique_tweets = self.duplicate_detector.find_duplicates_in_batch(
            [{'content': t['text'], **t} for t in tweets]
        )

        # Check against database for duplicates
        if self.config['duplicate_detection']['enabled']:
            days_back = self.config['duplicate_detection']['check_last_days']

            filtered = []
            for tweet in unique_tweets:
                if not self.db.is_content_duplicate(tweet['text'], days_back):
                    filtered.append(tweet)
                else:
                    self.logger.debug(f"  Skipping duplicate: {tweet['text'][:50]}...")

            unique_tweets = filtered

        self.logger.info(f"✅ {len(unique_tweets)} unique tweets ready for processing")

        return unique_tweets

    def generate_and_post_tweets(self, source_tweets: List[Dict]):
        """Generate and post new tweets"""
        self.logger.info("🤖 Generating AI tweets...")

        tweets_to_post = self.config['bot']['tweets_to_post_per_run']
        personality = self.config['bot']['personality']

        posted_count = 0

        # Group tweets by topic if there are many
        if len(source_tweets) > 5:
            # Take the most recent/relevant ones
            source_tweets = source_tweets[:5]

        for i in range(tweets_to_post):
            if not source_tweets:
                break

            # Generate tweet
            generated_tweet = self.ai.generate_tweet(
                source_tweets,
                personality=personality
            )

            if not generated_tweet:
                self.logger.warning(f"  Failed to generate tweet #{i+1}")
                continue

            self.logger.info(f"  Generated: {generated_tweet[:80]}...")

            # Check if generated tweet is duplicate
            if self.db.is_content_duplicate(generated_tweet):
                self.logger.warning("  Generated tweet is duplicate, skipping...")
                continue

            # Post tweet
            tweet_id = self.twitter.post_tweet(generated_tweet)

            if tweet_id:
                # Save to database
                source_ids = [str(t['id']) for t in source_tweets]
                self.db.add_posted_tweet(
                    content=generated_tweet,
                    source_tweet_ids=source_ids,
                    personality=personality,
                    tweet_id=tweet_id
                )

                # Mark source tweets as processed
                for tweet in source_tweets:
                    self.db.mark_tweet_processed(str(tweet['id']))

                posted_count += 1
                self.logger.info(f"  ✅ Posted tweet #{posted_count}")

        self.logger.info(f"📤 Posted {posted_count} tweet(s)")

    def _print_statistics(self):
        """Print bot statistics"""
        stats = self.db.get_statistics()

        self.logger.info("")
        self.logger.info("📊 Statistics:")
        self.logger.info(f"   Total collected: {stats['total_collected']}")
        self.logger.info(f"   Total posted: {stats['total_posted']}")
        self.logger.info(f"   Unprocessed: {stats['unprocessed']}")
        self.logger.info(f"   Today's posts: {stats['today_posts']}")
        self.logger.info("")

    def test_connection(self):
        """Test Twitter API connection"""
        self.logger.info("🔌 Testing Twitter API connection...")
        if self.twitter.verify_credentials():
            self.logger.info("✅ Twitter API connection successful!")
            return True
        else:
            self.logger.error("❌ Twitter API connection failed!")
            return False

    def dry_run(self):
        """Run bot in dry-run mode (no actual posting)"""
        self.logger.info("🧪 Running in DRY RUN mode (no tweets will be posted)")

        # Collect tweets
        collected_tweets = self.collect_tweets()

        if not collected_tweets:
            self.logger.info("No tweets collected")
            return

        # Process tweets
        processed_tweets = self.process_collected_tweets(collected_tweets)

        if not processed_tweets:
            self.logger.info("No tweets to process")
            return

        # Generate but don't post
        self.logger.info("Generating sample tweets...")
        personality = self.config['bot']['personality']

        for i in range(2):  # Generate 2 samples
            generated = self.ai.generate_tweet(
                processed_tweets[:5],
                personality=personality
            )

            if generated:
                self.logger.info(f"\n📝 Sample #{i+1}:")
                self.logger.info(f"   {generated}")

        self.logger.info("\n✅ Dry run completed")
