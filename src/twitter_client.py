"""
Twitter/X API Client using Tweepy
"""

import tweepy
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging


class TwitterClient:
    def __init__(self, api_key: str, api_secret: str, access_token: str,
                 access_token_secret: str, bearer_token: str):
        """
        Initialize Twitter API client

        Args:
            api_key: Twitter API Key
            api_secret: Twitter API Secret
            access_token: Access Token
            access_token_secret: Access Token Secret
            bearer_token: Bearer Token
        """
        self.logger = logging.getLogger(__name__)

        # Authentication
        self.auth = tweepy.OAuthHandler(api_key, api_secret)
        self.auth.set_access_token(access_token, access_token_secret)

        # API v1.1 (for posting tweets)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

        # API v2 (for reading tweets)
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

        self.logger.info("Twitter client initialized successfully")

    def verify_credentials(self) -> bool:
        """Verify API credentials are valid"""
        try:
            user = self.api.verify_credentials()
            self.logger.info(f"Authenticated as: @{user.screen_name}")
            return True
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username"""
        try:
            # Remove @ if present
            username = username.lstrip('@')

            user = self.client.get_user(username=username)
            if user.data:
                return user.data.id
            return None
        except Exception as e:
            self.logger.error(f"Error getting user ID for @{username}: {e}")
            return None

    def get_recent_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """
        Get recent tweets from a user

        Args:
            username: Twitter username (with or without @)
            max_results: Maximum number of tweets to retrieve (max 100)

        Returns:
            List of tweet dictionaries
        """
        try:
            username = username.lstrip('@')
            user_id = self.get_user_id(username)

            if not user_id:
                self.logger.warning(f"Could not find user: @{username}")
                return []

            # Get tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'text', 'public_metrics', 'lang'],
                exclude=['retweets', 'replies']  # Only original tweets
            )

            if not tweets.data:
                return []

            result = []
            for tweet in tweets.data:
                result.append({
                    'id': tweet.id,
                    'author': username,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'url': f"https://twitter.com/{username}/status/{tweet.id}",
                    'likes': tweet.public_metrics.get('like_count', 0),
                    'retweets': tweet.public_metrics.get('retweet_count', 0),
                    'lang': tweet.lang
                })

            self.logger.info(f"Retrieved {len(result)} tweets from @{username}")
            return result

        except Exception as e:
            self.logger.error(f"Error getting tweets from @{username}: {e}")
            return []

    def get_tweets_from_multiple_users(self, usernames: List[str],
                                       max_per_user: int = 10) -> List[Dict]:
        """
        Get recent tweets from multiple users

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

        # Sort by created_at (newest first)
        all_tweets.sort(key=lambda x: x['created_at'], reverse=True)

        self.logger.info(f"Retrieved total {len(all_tweets)} tweets from {len(usernames)} users")
        return all_tweets

    def post_tweet(self, text: str) -> Optional[str]:
        """
        Post a tweet

        Args:
            text: Tweet text (max 280 characters)

        Returns:
            Tweet ID if successful, None otherwise
        """
        try:
            if len(text) > 280:
                self.logger.warning(f"Tweet too long ({len(text)} chars), truncating...")
                text = text[:277] + "..."

            # Post using API v2
            response = self.client.create_tweet(text=text)

            if response.data:
                tweet_id = response.data['id']
                self.logger.info(f"✅ Tweet posted successfully! ID: {tweet_id}")
                return tweet_id
            else:
                self.logger.error("Failed to post tweet: No response data")
                return None

        except Exception as e:
            self.logger.error(f"Error posting tweet: {e}")
            return None

    def get_tweet_by_id(self, tweet_id: str) -> Optional[Dict]:
        """Get a specific tweet by ID"""
        try:
            tweet = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['created_at', 'text', 'author_id', 'public_metrics']
            )

            if tweet.data:
                return {
                    'id': tweet.data.id,
                    'text': tweet.data.text,
                    'created_at': tweet.data.created_at,
                    'author_id': tweet.data.author_id
                }
            return None

        except Exception as e:
            self.logger.error(f"Error getting tweet {tweet_id}: {e}")
            return None

    def filter_tweets_by_language(self, tweets: List[Dict], lang: str = 'tr') -> List[Dict]:
        """Filter tweets by language"""
        return [t for t in tweets if t.get('lang') == lang]

    def filter_tweets_by_date(self, tweets: List[Dict], hours_ago: int = 24) -> List[Dict]:
        """Filter tweets posted within the last N hours"""
        threshold = datetime.now(tweets[0]['created_at'].tzinfo) - timedelta(hours=hours_ago)
        return [t for t in tweets if t['created_at'] > threshold]
