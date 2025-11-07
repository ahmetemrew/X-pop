"""
Selenium-based Twitter/X Client (No API required!)
"""

import time
import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTwitterClient:
    def __init__(self, username: str, password: str, email: str = None,
                 headless: bool = True, cookies_path: str = "data/twitter_cookies.json"):
        """
        Initialize Selenium Twitter Client

        Args:
            username: Twitter username (without @)
            password: Twitter password
            email: Twitter email (for verification if needed)
            headless: Run browser in headless mode
            cookies_path: Path to save/load cookies
        """
        self.username = username
        self.password = password
        self.email = email
        self.cookies_path = cookies_path
        self.logger = logging.getLogger(__name__)

        # Initialize Chrome driver
        self.driver = self._init_driver(headless)
        self.wait = WebDriverWait(self.driver, 20)

        # Login
        self.is_logged_in = False
        self.login()

    def _init_driver(self, headless: bool) -> webdriver.Chrome:
        """Initialize Chrome WebDriver"""
        chrome_options = Options()

        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")

        # Additional options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # User agent
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Window size
        chrome_options.add_argument("--window-size=1920,1080")

        # Initialize driver
        driver_path = ChromeDriverManager().install()

        # Fix: Ensure we have the actual chromedriver binary, not THIRD_PARTY_NOTICES
        if 'THIRD_PARTY_NOTICES' in driver_path or not os.path.isfile(driver_path):
            # Look for actual chromedriver in the same directory
            driver_dir = os.path.dirname(driver_path)
            chromedriver_path = os.path.join(driver_dir, 'chromedriver')
            if os.path.isfile(chromedriver_path):
                driver_path = chromedriver_path
            else:
                # Try without extension
                for filename in os.listdir(driver_dir):
                    if filename.startswith('chromedriver') and 'THIRD_PARTY' not in filename:
                        driver_path = os.path.join(driver_dir, filename)
                        break

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Stealth
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })

        self.logger.info("Chrome driver initialized")
        return driver

    def _save_cookies(self):
        """Save cookies to file"""
        try:
            cookies = self.driver.get_cookies()
            os.makedirs(os.path.dirname(self.cookies_path), exist_ok=True)
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f)
            self.logger.info("Cookies saved")
        except Exception as e:
            self.logger.error(f"Error saving cookies: {e}")

    def _load_cookies(self) -> bool:
        """Load cookies from file"""
        try:
            if not os.path.exists(self.cookies_path):
                return False

            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)

            self.driver.get("https://twitter.com")
            time.sleep(2)

            for cookie in cookies:
                # Remove problematic keys
                cookie.pop('sameSite', None)
                self.driver.add_cookie(cookie)

            self.driver.refresh()
            time.sleep(3)

            self.logger.info("Cookies loaded")
            return True

        except Exception as e:
            self.logger.error(f"Error loading cookies: {e}")
            return False

    def login(self) -> bool:
        """
        Login to Twitter
        Uses cookies if available, otherwise performs fresh login
        """
        self.logger.info("Attempting to login to Twitter...")

        # Try loading cookies first
        if self._load_cookies():
            # Check if still logged in
            if self._verify_login():
                self.logger.info("✅ Logged in via cookies")
                self.is_logged_in = True
                return True

        # Fresh login
        self.logger.info("Performing fresh login...")

        try:
            # Go to login page
            self.driver.get("https://twitter.com/i/flow/login")
            time.sleep(3)

            # Enter username
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
            )
            username_input.send_keys(self.username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(2)

            # Check for unusual activity (email verification)
            try:
                email_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='ocfEnterTextTextInput']")
                if email_input and self.email:
                    self.logger.info("Email verification required")
                    email_input.send_keys(self.email)
                    email_input.send_keys(Keys.RETURN)
                    time.sleep(2)
            except NoSuchElementException:
                pass

            # Enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
            )
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)

            # Verify login
            if self._verify_login():
                self.logger.info("✅ Login successful")
                self._save_cookies()
                self.is_logged_in = True
                return True
            else:
                self.logger.error("❌ Login failed: Could not verify login")
                return False

        except Exception as e:
            self.logger.error(f"❌ Login error: {e}")
            return False

    def _verify_login(self) -> bool:
        """Verify if logged in successfully"""
        try:
            self.driver.get("https://twitter.com/home")
            time.sleep(3)

            # Check for home timeline
            try:
                self.driver.find_element(By.CSS_SELECTOR, "[data-testid='primaryColumn']")
                return True
            except NoSuchElementException:
                return False

        except Exception:
            return False

    def get_recent_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """
        Scrape recent tweets from a user

        Args:
            username: Twitter username (without @)
            max_results: Maximum number of tweets to collect

        Returns:
            List of tweet dictionaries
        """
        if not self.is_logged_in:
            self.logger.error("Not logged in!")
            return []

        username = username.lstrip('@')
        self.logger.info(f"Scraping tweets from @{username}")

        try:
            # Go to user profile
            self.driver.get(f"https://twitter.com/{username}")
            time.sleep(3)

            # Scroll and collect tweets
            tweets = []
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5

            while len(tweets) < max_results and scroll_attempts < max_scrolls:
                # Find tweet elements
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")

                for element in tweet_elements:
                    if len(tweets) >= max_results:
                        break

                    try:
                        # Extract tweet data
                        tweet_data = self._extract_tweet_data(element, username)
                        if tweet_data and tweet_data['id'] not in [t['id'] for t in tweets]:
                            tweets.append(tweet_data)

                    except Exception as e:
                        self.logger.debug(f"Error extracting tweet: {e}")
                        continue

                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Check if reached bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break

                last_height = new_height
                scroll_attempts += 1

            self.logger.info(f"Collected {len(tweets)} tweets from @{username}")
            return tweets[:max_results]

        except Exception as e:
            self.logger.error(f"Error scraping tweets from @{username}: {e}")
            return []

    def _extract_tweet_data(self, element, username: str) -> Optional[Dict]:
        """Extract data from a tweet element"""
        try:
            # Tweet text
            text_element = element.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
            text = text_element.text

            # Tweet link (to get ID)
            link_element = element.find_element(By.CSS_SELECTOR, "a[href*='/status/']")
            link = link_element.get_attribute('href')
            tweet_id = link.split('/status/')[-1].split('?')[0]

            # Time (relative)
            time_element = element.find_element(By.CSS_SELECTOR, "time")
            time_str = time_element.get_attribute('datetime')

            return {
                'id': tweet_id,
                'author': username,
                'text': text,
                'created_at': datetime.fromisoformat(time_str.replace('Z', '+00:00')),
                'url': link,
                'likes': 0,  # Could be scraped if needed
                'retweets': 0,
                'lang': 'tr'  # Assume Turkish
            }

        except Exception as e:
            return None

    def get_tweets_from_multiple_users(self, usernames: List[str],
                                       max_per_user: int = 10) -> List[Dict]:
        """
        Get tweets from multiple users

        Args:
            usernames: List of Twitter usernames
            max_per_user: Maximum tweets per user

        Returns:
            Combined list of tweets from all users
        """
        all_tweets = []

        for username in usernames:
            tweets = self.get_recent_tweets(username, max_per_user)
            all_tweets.extend(tweets)
            time.sleep(2)  # Rate limiting

        # Sort by created_at
        all_tweets.sort(key=lambda x: x['created_at'], reverse=True)

        self.logger.info(f"Retrieved total {len(all_tweets)} tweets from {len(usernames)} users")
        return all_tweets

    def post_tweet(self, text: str, image_path: str = None) -> Optional[str]:
        """
        Post a tweet with optional image

        Args:
            text: Tweet text (max 280 characters)
            image_path: Path to image file (optional)

        Returns:
            Tweet URL if successful, None otherwise
        """
        if not self.is_logged_in:
            self.logger.error("Not logged in!")
            return None

        try:
            if len(text) > 280:
                self.logger.warning(f"Tweet too long ({len(text)} chars), truncating...")
                text = text[:277] + "..."

            # Go to home page
            self.driver.get("https://twitter.com/home")
            time.sleep(3)

            # Upload image if provided
            if image_path and os.path.exists(image_path):
                try:
                    self.logger.info(f"📤 Uploading image: {image_path}")

                    # Find file input (hidden) for image upload
                    file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept*='image']")

                    # Send file path to input
                    file_input.send_keys(os.path.abspath(image_path))
                    time.sleep(3)  # Wait for upload

                    self.logger.info(f"✅ Image uploaded!")

                except Exception as e:
                    self.logger.error(f"Failed to upload image: {e}")
                    # Continue without image

            # Find tweet box
            tweet_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']"))
            )

            # Click and enter text
            tweet_box.click()
            time.sleep(1)
            tweet_box.send_keys(text)
            time.sleep(2)

            # Find and click post button
            post_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='tweetButtonInline']"))
            )
            post_button.click()

            time.sleep(3)

            img_status = " (with image)" if image_path else ""
            self.logger.info(f"✅ Tweet posted successfully{img_status}!")
            return f"https://twitter.com/{self.username}"  # Can't get exact tweet ID easily

        except Exception as e:
            self.logger.error(f"Error posting tweet: {e}")
            return None

    def filter_tweets_by_language(self, tweets: List[Dict], lang: str = 'tr') -> List[Dict]:
        """Filter tweets by language (basic)"""
        # For Selenium version, we assume all are Turkish
        return tweets

    def filter_tweets_by_date(self, tweets: List[Dict], hours_ago: int = 24) -> List[Dict]:
        """Filter tweets posted within the last N hours"""
        from datetime import timedelta
        threshold = datetime.now(tweets[0]['created_at'].tzinfo) - timedelta(hours=hours_ago)
        return [t for t in tweets if t['created_at'] > threshold]

    def close(self):
        """Close the browser"""
        try:
            self.driver.quit()
            self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
