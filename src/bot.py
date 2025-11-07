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
from .selenium_twitter_client import SeleniumTwitterClient
from .ai_generator import AIGenerator
from .database import Database
from .duplicate_detector import DuplicateDetector
from .human_behavior import HumanBehavior, SmartScheduler
from .image_fetcher import ImageFetcher


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

        # Initialize Twitter client (API or Selenium based on config)
        self.mode = self.config.get('mode', 'api')
        self.twitter = self._init_twitter_client()

        # Initialize AI generator
        self.ai = self._init_ai_generator()

        # Set personality
        personality = self.config['bot']['personality']
        self.ai.set_personality(personality)

        # Initialize human behavior simulator
        human_behavior_config = self.config.get('human_behavior', {})
        self.human_behavior = HumanBehavior(human_behavior_config)

        # Initialize smart scheduler
        base_interval = self.config['bot']['check_interval']
        self.smart_scheduler = SmartScheduler(base_interval)

        # Initialize image fetcher
        image_config = self.config.get('images', {})
        self.image_fetcher = ImageFetcher() if image_config.get('enabled', True) else None

        mode_label = "API" if self.mode == 'api' else "Selenium (No API)"
        self.logger.info(f"✅ Bot initialized with personality: {personality}, mode: {mode_label}")

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

    def _init_twitter_client(self):
        """Initialize Twitter client (API or Selenium)"""
        try:
            if self.mode == 'api':
                self.logger.info("Initializing Twitter API client...")
                return TwitterClient(
                    api_key=os.getenv('TWITTER_API_KEY'),
                    api_secret=os.getenv('TWITTER_API_SECRET'),
                    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                    bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
                )
            elif self.mode == 'selenium':
                self.logger.info("Initializing Selenium Twitter client...")
                return SeleniumTwitterClient(
                    username=os.getenv('TWITTER_USERNAME'),
                    password=os.getenv('TWITTER_PASSWORD'),
                    email=os.getenv('TWITTER_EMAIL'),
                    headless=os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
                )
            else:
                raise ValueError(f"Invalid mode: {self.mode}. Must be 'api' or 'selenium'")
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {e}")
            raise

    def _init_ai_generator(self) -> AIGenerator:
        """Initialize AI generator"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")

            model = self.config['ai']['model']
            temperature = self.config['ai'].get('temperature', 0.7)
            max_tokens = self.config['ai'].get('max_tokens', 280)

            self.logger.info(f"Initializing AI with model: {model}, temp: {temperature}")

            ai_gen = AIGenerator(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )

            self.logger.info("✅ AI generator initialized successfully")
            return ai_gen

        except Exception as e:
            self.logger.error(f"Failed to initialize AI generator: {e}", exc_info=True)
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
        """Generate and post new tweets with human behavior simulation"""
        self.logger.info("🤖 Generating AI tweets...")

        # Random delay before generation (human thinking time)
        delays = self.human_behavior.get_random_action_delays()
        import time
        time.sleep(delays['before_generate'])

        tweets_to_post = self.config['bot']['tweets_to_post_per_run']
        personality = self.config['bot']['personality']

        posted_count = 0

        # Random skip chance (sometimes humans don't post)
        if self.human_behavior.should_skip_this_run():
            self.logger.info("🎲 Randomly skipping this run (human behavior)")
            return

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

            # Add human variance to text (sometimes small changes)
            generated_tweet = self.human_behavior.add_human_variance_to_text(generated_tweet)

            self.logger.info(f"  Generated: {generated_tweet[:80]}...")

            # Typing simulation delay
            typing_delay = self.human_behavior.typing_simulation(len(generated_tweet))
            time.sleep(min(typing_delay, 10))  # Max 10 seconds

            # Check if generated tweet is duplicate
            if self.db.is_content_duplicate(generated_tweet):
                self.logger.warning("  Generated tweet is duplicate, skipping...")
                continue

            # Fetch image if enabled
            image_path = None
            if self.image_fetcher:
                try:
                    self.logger.info("🖼️  Searching for related image...")
                    image_path = self.image_fetcher.fetch_image_for_tweet(generated_tweet)

                    if image_path:
                        self.logger.info(f"✅ Image found: {image_path}")
                    else:
                        self.logger.info("ℹ️  No image found, posting without image")

                except Exception as e:
                    self.logger.error(f"Image fetch error: {e}")

            # Delay before posting (human hesitation)
            time.sleep(delays['before_post'])

            # Post tweet with image
            tweet_id = self.twitter.post_tweet(generated_tweet, image_path=image_path)

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

                # Delay after posting (human behavior)
                time.sleep(delays['after_post'])

                # Cleanup image if was downloaded
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass

        self.logger.info(f"📤 Posted {posted_count} tweet(s)")

        # Cleanup old images
        if self.image_fetcher:
            self.image_fetcher.cleanup_old_images()

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
        """Test Twitter connection (API or Selenium)"""
        self.logger.info(f"🔌 Testing Twitter connection ({self.mode} mode)...")

        if self.mode == 'api':
            if self.twitter.verify_credentials():
                self.logger.info("✅ Twitter API connection successful!")
                return True
            else:
                self.logger.error("❌ Twitter API connection failed!")
                return False
        elif self.mode == 'selenium':
            if self.twitter.is_logged_in:
                self.logger.info("✅ Selenium Twitter connection successful!")
                return True
            else:
                self.logger.error("❌ Selenium Twitter connection failed!")
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
