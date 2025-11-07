"""
Database module for storing tweets and tracking duplicates
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib


class Database:
    def __init__(self, db_path: str = "data/tweets.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for collected tweets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collected_tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id TEXT UNIQUE,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                url TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        """)

        # Table for posted tweets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posted_tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                source_tweet_ids TEXT,
                personality TEXT,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tweet_id TEXT
            )
        """)

        # Index for faster duplicate detection
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash
            ON collected_tweets(content_hash)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_posted_hash
            ON posted_tweets(content_hash)
        """)

        conn.commit()
        conn.close()

    def _hash_content(self, content: str) -> str:
        """Generate hash for content to detect duplicates"""
        # Normalize content: lowercase, remove extra spaces
        normalized = " ".join(content.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()

    def add_collected_tweet(self, tweet_id: str, author: str, content: str, url: str = None) -> bool:
        """
        Add a collected tweet to database
        Returns True if added, False if duplicate
        """
        content_hash = self._hash_content(content)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO collected_tweets (tweet_id, author, content, content_hash, url)
                VALUES (?, ?, ?, ?, ?)
            """, (tweet_id, author, content, content_hash, url))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Duplicate tweet_id
            return False

    def is_content_duplicate(self, content: str, days_back: int = 7) -> bool:
        """
        Check if similar content was already collected or posted
        """
        content_hash = self._hash_content(content)
        date_threshold = datetime.now() - timedelta(days=days_back)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check collected tweets
        cursor.execute("""
            SELECT COUNT(*) FROM collected_tweets
            WHERE content_hash = ? AND collected_at > ?
        """, (content_hash, date_threshold))

        collected_count = cursor.fetchone()[0]

        # Check posted tweets
        cursor.execute("""
            SELECT COUNT(*) FROM posted_tweets
            WHERE content_hash = ? AND posted_at > ?
        """, (content_hash, date_threshold))

        posted_count = cursor.fetchone()[0]

        conn.close()

        return (collected_count + posted_count) > 1  # >1 because current one counts

    def get_unprocessed_tweets(self, limit: int = 10) -> List[Dict]:
        """Get unprocessed tweets for AI generation"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM collected_tweets
            WHERE processed = FALSE
            ORDER BY collected_at DESC
            LIMIT ?
        """, (limit,))

        tweets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return tweets

    def mark_tweet_processed(self, tweet_id: str):
        """Mark a tweet as processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE collected_tweets
            SET processed = TRUE
            WHERE tweet_id = ?
        """, (tweet_id,))

        conn.commit()
        conn.close()

    def add_posted_tweet(self, content: str, source_tweet_ids: List[str],
                        personality: str, tweet_id: str = None) -> int:
        """
        Add a posted tweet to database
        Returns the database ID
        """
        content_hash = self._hash_content(content)
        source_ids_json = json.dumps(source_tweet_ids)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO posted_tweets (content, content_hash, source_tweet_ids, personality, tweet_id)
            VALUES (?, ?, ?, ?, ?)
        """, (content, content_hash, source_ids_json, personality, tweet_id))

        post_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return post_id

    def get_recent_posts(self, days: int = 7, limit: int = 50) -> List[Dict]:
        """Get recent posted tweets"""
        date_threshold = datetime.now() - timedelta(days=days)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM posted_tweets
            WHERE posted_at > ?
            ORDER BY posted_at DESC
            LIMIT ?
        """, (date_threshold, limit))

        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return posts

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total collected
        cursor.execute("SELECT COUNT(*) FROM collected_tweets")
        total_collected = cursor.fetchone()[0]

        # Total posted
        cursor.execute("SELECT COUNT(*) FROM posted_tweets")
        total_posted = cursor.fetchone()[0]

        # Unprocessed
        cursor.execute("SELECT COUNT(*) FROM collected_tweets WHERE processed = FALSE")
        unprocessed = cursor.fetchone()[0]

        # Today's posts
        today = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) FROM posted_tweets
            WHERE DATE(posted_at) = ?
        """, (today,))
        today_posts = cursor.fetchone()[0]

        conn.close()

        return {
            "total_collected": total_collected,
            "total_posted": total_posted,
            "unprocessed": unprocessed,
            "today_posts": today_posts
        }
