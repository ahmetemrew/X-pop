"""
Advanced duplicate detection using similarity algorithms
"""

from typing import List, Dict
from difflib import SequenceMatcher


class DuplicateDetector:
    def __init__(self, threshold: float = 0.85):
        """
        Initialize duplicate detector

        Args:
            threshold: Similarity threshold (0.0 to 1.0).
                      0.85 means 85% similar content is considered duplicate
        """
        self.threshold = threshold

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        Returns a score between 0.0 (completely different) and 1.0 (identical)
        """
        # Normalize texts
        text1 = self._normalize_text(text1)
        text2 = self._normalize_text(text2)

        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, text1, text2).ratio()

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        import re
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove mentions and hashtags for comparison
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text.strip()

    def is_similar_to_any(self, content: str, existing_contents: List[str]) -> tuple[bool, float]:
        """
        Check if content is similar to any existing content

        Returns:
            (is_duplicate, max_similarity_score)
        """
        if not existing_contents:
            return False, 0.0

        max_similarity = 0.0

        for existing in existing_contents:
            similarity = self.calculate_similarity(content, existing)
            max_similarity = max(max_similarity, similarity)

            if similarity >= self.threshold:
                return True, similarity

        return False, max_similarity

    def find_duplicates_in_batch(self, tweets: List[Dict[str, str]]) -> List[Dict]:
        """
        Find duplicates within a batch of tweets

        Args:
            tweets: List of dicts with 'content' key

        Returns:
            List of unique tweets (duplicates removed)
        """
        unique_tweets = []
        seen_contents = []

        for tweet in tweets:
            content = tweet.get('content', '')

            is_dup, similarity = self.is_similar_to_any(content, seen_contents)

            if not is_dup:
                unique_tweets.append(tweet)
                seen_contents.append(content)
            else:
                print(f"  ⚠️  Duplicate detected (similarity: {similarity:.2%})")

        return unique_tweets

    def extract_unique_topics(self, tweets: List[str]) -> List[str]:
        """
        Extract unique topics from a list of tweets by grouping similar content
        """
        if not tweets:
            return []

        topics = []
        grouped = []

        for tweet in tweets:
            # Check if this tweet is similar to any existing topic
            is_grouped = False
            for topic_group in grouped:
                if self.calculate_similarity(tweet, topic_group[0]) >= self.threshold:
                    topic_group.append(tweet)
                    is_grouped = True
                    break

            if not is_grouped:
                grouped.append([tweet])

        # Take the first tweet from each group as representative
        topics = [group[0] for group in grouped]

        return topics
