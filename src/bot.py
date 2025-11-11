"""
Main Bot Orchestrator
"""

import os
import yaml
import logging
import signal
import atexit
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from .twitter_client import TwitterClient
from .selenium_twitter_client import SeleniumTwitterClient
from .ai_generator import AIGenerator
from .database import Database
from .duplicate_detector import DuplicateDetector
from .human_behavior import HumanBehavior, SmartScheduler
from .image_fetcher import ImageFetcher
from .utils import validate_config, check_disk_space, cleanup_old_files, safe_file_operation


class XPopBot:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the X-Pop Bot"""
        self._shutdown_requested = False
        self.twitter: Optional[TwitterClient] = None
        self.ai: Optional[AIGenerator] = None
        self.db: Optional[Database] = None

        try:
            # Load environment variables
            load_dotenv()

            # Setup logging
            self._setup_logging()

            self.logger.info("🚀 Initializing X-Pop Bot...")

            # Check disk space
            if not check_disk_space(min_mb=100):
                self.logger.warning("⚠️ Low disk space! Consider cleaning up.")

            # Load and validate configuration
            def load_config():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)

            raw_config = safe_file_operation(load_config)
            self.config = validate_config(raw_config)

            self.logger.info("✅ Configuration validated")

            # Create required directories
            os.makedirs('logs', exist_ok=True)
            os.makedirs('data', exist_ok=True)
            os.makedirs('downloads', exist_ok=True)

            # Initialize components
            try:
                self.db = Database()
                self.logger.info("✅ Database initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize database: {e}")
                self.logger.warning("⚠️ Bot cannot run without database!")
                raise  # Database is critical, must raise

            try:
                self.duplicate_detector = DuplicateDetector(
                    threshold=self.config['duplicate_detection']['similarity_threshold']
                )
                self.logger.info("✅ Duplicate detector initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to init duplicate detector: {e}")
                self.logger.warning("⚠️ Bot will not check for duplicates")
                self.duplicate_detector = None

            # Initialize Twitter client (API or Selenium based on config)
            self.mode = self.config.get('mode', 'selenium')
            self.twitter = self._init_twitter_client()

            # Initialize AI generator
            self.ai = self._init_ai_generator()

            # Set personality (only if AI is available)
            if self.ai:
                try:
                    personality = self.config['bot']['personality']
                    self.ai.set_personality(personality)
                    self.logger.info(f"✅ Personality set to: {personality}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to set personality: {e}")
                    self.logger.warning("⚠️ AI will use default personality")

            # Initialize human behavior simulator
            try:
                human_behavior_config = self.config.get('human_behavior', {})
                self.human_behavior = HumanBehavior(human_behavior_config)
                self.logger.info("✅ Human behavior simulator initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to init human behavior: {e}")
                self.logger.warning("⚠️ Bot will use default behavior patterns")
                self.human_behavior = None

            # Initialize smart scheduler
            try:
                base_interval = self.config['bot']['check_interval']
                self.smart_scheduler = SmartScheduler(base_interval)
                self.logger.info("✅ Smart scheduler initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to init scheduler: {e}")
                self.logger.warning("⚠️ Bot will use fixed intervals")
                self.smart_scheduler = None

            # Initialize image fetcher
            try:
                image_config = self.config.get('images', {})
                self.image_fetcher = ImageFetcher() if image_config.get('enabled', True) else None
                if self.image_fetcher:
                    self.logger.info("✅ Image fetcher initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to init image fetcher: {e}")
                self.logger.warning("⚠️ Bot will post tweets without images")
                self.image_fetcher = None

            # Register cleanup handlers
            atexit.register(self.cleanup)
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)

            # Cleanup old files
            try:
                cleanup_old_files('logs', days=7, pattern='*.log')
                cleanup_old_files('downloads', days=1, pattern='*')
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to cleanup old files: {e}")

            mode_label = "API" if self.mode == 'api' else "Selenium (No API)"
            personality_str = self.config.get('bot', {}).get('personality', 'unknown')

            # Summary
            self.logger.info("=" * 60)
            self.logger.info(f"✅ Bot initialized successfully!")
            self.logger.info(f"   Mode: {mode_label}")
            self.logger.info(f"   Personality: {personality_str}")
            self.logger.info(f"   Twitter Client: {'✅' if self.twitter else '❌ (degraded mode)'}")
            self.logger.info(f"   AI Generator: {'✅' if self.ai else '❌ (monitoring only)'}")
            self.logger.info(f"   Database: ✅")
            self.logger.info(f"   Image Fetcher: {'✅' if self.image_fetcher else '❌'}")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"Fatal error during initialization: {e}", exc_info=True)
            self.cleanup()
            raise

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
        """Initialize Twitter client (API or Selenium) - NON-FATAL"""
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

                # Try to initialize, but don't crash if it fails
                try:
                    client = SeleniumTwitterClient(
                        username=os.getenv('TWITTER_USERNAME'),
                        password=os.getenv('TWITTER_PASSWORD'),
                        email=os.getenv('TWITTER_EMAIL'),
                        headless=os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
                    )

                    if client.is_logged_in:
                        self.logger.info("✅ Twitter client logged in successfully")
                        return client
                    else:
                        self.logger.warning("⚠️ Twitter client initialized but NOT logged in")
                        self.logger.warning("⚠️ Bot will run in DEGRADED mode (no Twitter functionality)")
                        return None

                except Exception as selenium_error:
                    self.logger.error(f"❌ Selenium initialization failed: {selenium_error}")
                    self.logger.warning("=" * 60)
                    self.logger.warning("⚠️ BOT CONTINUING IN DEGRADED MODE")
                    self.logger.warning("Twitter features will be DISABLED")
                    self.logger.warning("")
                    self.logger.warning("To fix Twitter login:")
                    self.logger.warning("  1. Use cookie-based login (see COOKIE_LOGIN_GUIDE.md)")
                    self.logger.warning("  2. OR fix username/password in .env")
                    self.logger.warning("  3. OR disable Selenium and use API mode")
                    self.logger.warning("=" * 60)
                    return None
            else:
                raise ValueError(f"Invalid mode: {self.mode}. Must be 'api' or 'selenium'")

        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {e}", exc_info=True)
            self.logger.warning("⚠️ Bot will continue WITHOUT Twitter functionality")
            return None

    def _init_ai_generator(self) -> Optional[AIGenerator]:
        """Initialize AI generator - NON-FATAL"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                self.logger.error("❌ GROQ_API_KEY not found in environment variables")
                self.logger.warning("⚠️ Bot will run WITHOUT AI generation (manual mode)")
                return None

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
            self.logger.error(f"❌ Failed to initialize AI generator: {e}", exc_info=True)
            self.logger.warning("=" * 60)
            self.logger.warning("⚠️ BOT CONTINUING WITHOUT AI GENERATION")
            self.logger.warning("Bot will run in monitoring mode only")
            self.logger.warning("")
            self.logger.warning("To fix AI generation:")
            self.logger.warning("  1. Check GROQ_API_KEY in .env file")
            self.logger.warning("  2. Verify API key is valid at https://console.groq.com/keys")
            self.logger.warning("  3. Check internet connection")
            self.logger.warning("=" * 60)
            return None

    def run_cycle(self):
        """Run one complete bot cycle"""
        # Check if shutdown requested
        if self._shutdown_requested:
            self.logger.info("⚠️ Shutdown requested, skipping cycle")
            return

        # Health check
        if not self.is_healthy():
            self.logger.error("❌ Health check failed, skipping cycle")
            return

        self.logger.info("=" * 60)
        self.logger.info(f"🔄 Starting bot cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)

        try:
            # Step 1: Collect tweets
            if self._shutdown_requested:
                return

            collected_tweets = self.collect_tweets()

            if not collected_tweets:
                self.logger.info("📭 No new tweets collected")
                self._print_statistics()
                return

            # Step 2: Process and filter tweets
            if self._shutdown_requested:
                return

            processed_tweets = self.process_collected_tweets(collected_tweets)

            if not processed_tweets:
                self.logger.info("⚠️  No tweets to process after filtering")
                self._print_statistics()
                return

            # Step 3: Generate and post new tweets
            if self._shutdown_requested:
                return

            self.generate_and_post_tweets(processed_tweets)

            # Step 4: Print statistics
            self._print_statistics()

            self.logger.info("✅ Cycle completed successfully")

        except KeyboardInterrupt:
            self.logger.info("⚠️ Interrupted by user")
            self._shutdown_requested = True
        except Exception as e:
            self.logger.error(f"❌ Error in bot cycle: {e}", exc_info=True)

    def collect_tweets(self) -> List[Dict]:
        """Collect tweets from monitored accounts - SAFE"""
        self.logger.info("📡 Collecting tweets from monitored accounts...")

        # Check if Twitter client is available
        if not self.twitter:
            self.logger.warning("⚠️ Twitter client not available, cannot collect tweets")
            self.logger.warning("⚠️ Bot running in DEGRADED mode")
            return []

        try:
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
                try:
                    if self.db.add_collected_tweet(
                        tweet_id=str(tweet['id']),
                        author=tweet['author'],
                        content=tweet['text'],
                        url=tweet['url']
                    ):
                        new_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to store tweet {tweet.get('id')}: {e}")
                    continue

            self.logger.info(f"💾 Stored {new_count} new tweets in database")

            return all_tweets

        except Exception as e:
            self.logger.error(f"❌ Error collecting tweets: {e}", exc_info=True)
            return []

    def process_collected_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """Process and filter collected tweets - SAFE"""
        self.logger.info("🔍 Processing collected tweets...")

        try:
            # Remove duplicates within the batch
            if self.duplicate_detector:
                unique_tweets = self.duplicate_detector.find_duplicates_in_batch(
                    [{'content': t['text'], **t} for t in tweets]
                )
            else:
                self.logger.warning("⚠️ Duplicate detector not available, skipping batch dedup")
                unique_tweets = tweets

            # Check against database for duplicates
            if self.config.get('duplicate_detection', {}).get('enabled', True):
                try:
                    days_back = self.config['duplicate_detection']['check_last_days']

                    filtered = []
                    for tweet in unique_tweets:
                        try:
                            if not self.db.is_content_duplicate(tweet['text'], days_back):
                                filtered.append(tweet)
                            else:
                                self.logger.debug(f"  Skipping duplicate: {tweet['text'][:50]}...")
                        except Exception as e:
                            self.logger.warning(f"⚠️ Error checking duplicate for tweet: {e}")
                            # Include the tweet if we can't check
                            filtered.append(tweet)

                    unique_tweets = filtered
                except Exception as e:
                    self.logger.warning(f"⚠️ Error in duplicate detection: {e}")
                    # Continue with all tweets if duplicate detection fails

            self.logger.info(f"✅ {len(unique_tweets)} unique tweets ready for processing")
            return unique_tweets

        except Exception as e:
            self.logger.error(f"❌ Error processing tweets: {e}", exc_info=True)
            # Return original tweets if processing fails
            return tweets

    def generate_and_post_tweets(self, source_tweets: List[Dict]):
        """Generate and post new tweets with human behavior simulation - SAFE"""
        self.logger.info("🤖 Generating AI tweets...")

        # Check if AI is available
        if not self.ai:
            self.logger.warning("⚠️ AI generator not available, cannot generate tweets")
            self.logger.info("📝 Bot running in monitoring-only mode")
            return

        # Random delay before generation (human thinking time)
        import time
        if self.human_behavior:
            try:
                delays = self.human_behavior.get_random_action_delays()
                time.sleep(delays['before_generate'])
            except Exception as e:
                self.logger.warning(f"⚠️ Error in human behavior delays: {e}")
                time.sleep(2)  # Default delay
        else:
            time.sleep(2)  # Default delay if no human behavior

        tweets_to_post = self.config.get('bot', {}).get('tweets_to_post_per_run', 1)
        personality = self.config.get('bot', {}).get('personality', 'yorumcu')

        posted_count = 0

        # Random skip chance (sometimes humans don't post)
        if self.human_behavior:
            try:
                if self.human_behavior.should_skip_this_run():
                    self.logger.info("🎲 Randomly skipping this run (human behavior)")
                    return
            except Exception as e:
                self.logger.warning(f"⚠️ Error in skip check: {e}")

        # Group tweets by topic if there are many
        if len(source_tweets) > 5:
            # Take the most recent/relevant ones
            source_tweets = source_tweets[:5]

        for i in range(tweets_to_post):
            if not source_tweets:
                break

            # Generate tweet - SAFE
            try:
                generated_tweet = self.ai.generate_tweet(
                    source_tweets,
                    personality=personality
                )

                if not generated_tweet:
                    self.logger.warning(f"  Failed to generate tweet #{i+1}")
                    continue
            except Exception as e:
                self.logger.error(f"❌ Error generating tweet #{i+1}: {e}")
                continue

            # Add human variance to text (sometimes small changes)
            if self.human_behavior:
                try:
                    generated_tweet = self.human_behavior.add_human_variance_to_text(generated_tweet)
                except Exception as e:
                    self.logger.warning(f"⚠️ Error adding human variance: {e}")

            self.logger.info(f"  Generated: {generated_tweet[:80]}...")

            # Typing simulation delay
            if self.human_behavior:
                try:
                    typing_delay = self.human_behavior.typing_simulation(len(generated_tweet))
                    time.sleep(min(typing_delay, 10))  # Max 10 seconds
                except Exception as e:
                    self.logger.warning(f"⚠️ Error in typing simulation: {e}")
                    time.sleep(2)  # Default delay
            else:
                time.sleep(2)  # Default delay

            # Check if generated tweet is duplicate - SAFE
            try:
                if self.db and self.db.is_content_duplicate(generated_tweet):
                    self.logger.warning("  Generated tweet is duplicate, skipping...")
                    continue
            except Exception as e:
                self.logger.warning(f"⚠️ Error checking duplicate: {e}")
                # Continue anyway if duplicate check fails

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
            if self.human_behavior:
                try:
                    time.sleep(delays['before_post'])
                except:
                    time.sleep(2)
            else:
                time.sleep(2)

            # Post tweet with image - SAFE
            tweet_id = None
            if self.twitter:
                try:
                    tweet_id = self.twitter.post_tweet(generated_tweet, image_path=image_path)
                except Exception as e:
                    self.logger.error(f"❌ Failed to post tweet: {e}")
                    tweet_id = None
            else:
                self.logger.warning("⚠️ Twitter client not available, cannot post tweet")
                self.logger.info(f"📝 Would have posted: {generated_tweet[:100]}...")

            if tweet_id:
                # Save to database - SAFE
                try:
                    source_ids = [str(t['id']) for t in source_tweets]
                    self.db.add_posted_tweet(
                        content=generated_tweet,
                        source_tweet_ids=source_ids,
                        personality=personality,
                        tweet_id=tweet_id
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to save posted tweet to DB: {e}")

                # Mark source tweets as processed - SAFE
                try:
                    for tweet in source_tweets:
                        self.db.mark_tweet_processed(str(tweet['id']))
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to mark tweets as processed: {e}")

                posted_count += 1
                self.logger.info(f"  ✅ Posted tweet #{posted_count}")

                # Delay after posting (human behavior)
                if self.human_behavior:
                    try:
                        time.sleep(delays['after_post'])
                    except:
                        time.sleep(2)
                else:
                    time.sleep(2)

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
        """Print bot statistics - SAFE"""
        try:
            if not self.db:
                self.logger.warning("⚠️ Database not available, cannot show statistics")
                return

            stats = self.db.get_statistics()

            self.logger.info("")
            self.logger.info("📊 Statistics:")
            self.logger.info(f"   Total collected: {stats.get('total_collected', 0)}")
            self.logger.info(f"   Total posted: {stats.get('total_posted', 0)}")
            self.logger.info(f"   Unprocessed: {stats.get('unprocessed', 0)}")
            self.logger.info(f"   Today's posts: {stats.get('today_posts', 0)}")
            self.logger.info("")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get statistics: {e}")

    def test_connection(self):
        """Test Twitter connection (API or Selenium) - SAFE"""
        try:
            self.logger.info(f"🔌 Testing Twitter connection ({self.mode} mode)...")

            if not self.twitter:
                self.logger.warning("⚠️ Twitter client not initialized")
                return False

            if self.mode == 'api':
                try:
                    if self.twitter.verify_credentials():
                        self.logger.info("✅ Twitter API connection successful!")
                        return True
                    else:
                        self.logger.error("❌ Twitter API connection failed!")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ Error testing API connection: {e}")
                    return False

            elif self.mode == 'selenium':
                try:
                    if self.twitter.is_logged_in:
                        self.logger.info("✅ Selenium Twitter connection successful!")
                        return True
                    else:
                        self.logger.error("❌ Selenium Twitter connection failed!")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ Error testing Selenium connection: {e}")
                    return False

            return False

        except Exception as e:
            self.logger.error(f"❌ Error in test_connection: {e}")
            return False

    def dry_run(self):
        """Run bot in dry-run mode (no actual posting) - SAFE"""
        try:
            self.logger.info("🧪 Running in DRY RUN mode (no tweets will be posted)")

            # Collect tweets
            try:
                collected_tweets = self.collect_tweets()

                if not collected_tweets:
                    self.logger.info("No tweets collected")
                    return
            except Exception as e:
                self.logger.error(f"❌ Error collecting tweets: {e}")
                return

            # Process tweets
            try:
                processed_tweets = self.process_collected_tweets(collected_tweets)

                if not processed_tweets:
                    self.logger.info("No tweets to process")
                    return
            except Exception as e:
                self.logger.error(f"❌ Error processing tweets: {e}")
                return

            # Generate but don't post
            if not self.ai:
                self.logger.warning("⚠️ AI not available, cannot generate sample tweets")
                return

            self.logger.info("Generating sample tweets...")
            personality = self.config.get('bot', {}).get('personality', 'yorumcu')

            for i in range(2):  # Generate 2 samples
                try:
                    generated = self.ai.generate_tweet(
                        processed_tweets[:5],
                        personality=personality
                    )

                    if generated:
                        self.logger.info(f"\n📝 Sample #{i+1}:")
                        self.logger.info(f"   {generated}")
                    else:
                        self.logger.warning(f"⚠️ Failed to generate sample #{i+1}")
                except Exception as e:
                    self.logger.error(f"❌ Error generating sample #{i+1}: {e}")

            self.logger.info("\n✅ Dry run completed")

        except Exception as e:
            self.logger.error(f"❌ Error in dry_run: {e}", exc_info=True)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        signal_name = 'SIGTERM' if signum == signal.SIGTERM else 'SIGINT'
        self.logger.info(f"\n⚠️ Received {signal_name}, shutting down gracefully...")
        self._shutdown_requested = True
        self.cleanup()

    def cleanup(self):
        """Clean up resources before shutdown"""
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            return

        self.logger.info("🧹 Cleaning up resources...")

        try:
            # Close Selenium driver if exists
            if self.twitter and hasattr(self.twitter, 'driver'):
                try:
                    self.twitter.driver.quit()
                    self.logger.info("✅ Closed Selenium driver")
                except Exception as e:
                    self.logger.warning(f"Error closing Selenium driver: {e}")

            # Close database connection
            if self.db and hasattr(self.db, 'close'):
                try:
                    self.db.close()
                    self.logger.info("✅ Closed database connection")
                except Exception as e:
                    self.logger.warning(f"Error closing database: {e}")

            # Cleanup image fetcher
            if self.image_fetcher:
                try:
                    self.image_fetcher.cleanup_old_images()
                    self.logger.info("✅ Cleaned up images")
                except Exception as e:
                    self.logger.warning(f"Error cleaning images: {e}")

            # Cleanup old logs
            try:
                cleanup_old_files('logs', days=7, pattern='*.log')
                cleanup_old_files('downloads', days=1, pattern='*')
            except Exception as e:
                self.logger.warning(f"Error cleaning old files: {e}")

            self.logger.info("✅ Cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

        finally:
            self._cleanup_done = True

    def is_healthy(self) -> bool:
        """Check if bot is healthy and ready to run - SAFE"""
        try:
            # Check disk space
            try:
                if not check_disk_space(min_mb=50):
                    self.logger.warning("⚠️ Low disk space")
                    # Don't fail - just warn
            except Exception as e:
                self.logger.warning(f"⚠️ Could not check disk space: {e}")

            # Check database (CRITICAL - must have)
            if not self.db:
                self.logger.error("❌ Database not initialized - CRITICAL")
                return False

            # Check config (CRITICAL - must have)
            if not self.config:
                self.logger.error("❌ Config not loaded - CRITICAL")
                return False

            # AI and Twitter are OPTIONAL - bot can run in monitoring/degraded mode
            if not self.ai:
                self.logger.warning("⚠️ AI generator not available (monitoring mode only)")
                # Don't return False - let bot continue

            if not self.twitter:
                self.logger.warning("⚠️ Twitter client not available (degraded mode)")
                # Don't return False - let bot continue

            # If we have neither AI nor Twitter, bot is pretty useless but won't crash
            if not self.ai and not self.twitter:
                self.logger.warning("⚠️ Both AI and Twitter unavailable - bot in minimal mode")

            return True

        except Exception as e:
            self.logger.error(f"❌ Health check error: {e}")
            return False
