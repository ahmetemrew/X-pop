"""
AI Tweet Generator using Groq API
"""

from groq import Groq
import logging
from typing import List, Dict, Optional
import yaml


class AIGenerator:
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile",
                 temperature: float = 0.7, max_tokens: int = 280):
        """
        Initialize AI Generator with Groq

        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.1-70b-versatile)
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum tokens for response
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = logging.getLogger(__name__)

        self.personalities = self._load_personalities()
        self.current_personality = None

    def _load_personalities(self) -> Dict:
        """Load personality configurations"""
        try:
            with open('config/personalities.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading personalities: {e}")
            return {}

    def set_personality(self, personality_name: str):
        """Set the bot's personality"""
        if personality_name in self.personalities:
            self.current_personality = self.personalities[personality_name]
            self.logger.info(f"Personality set to: {personality_name}")
        else:
            self.logger.warning(f"Personality '{personality_name}' not found. Using default.")
            self.current_personality = None

    def generate_tweet(self, source_tweets: List[Dict], personality: str = None) -> Optional[str]:
        """
        Generate a tweet based on source tweets

        Args:
            source_tweets: List of source tweet dictionaries
            personality: Personality to use (overrides current)

        Returns:
            Generated tweet text or None if failed
        """
        if personality:
            self.set_personality(personality)

        if not self.current_personality:
            self.logger.error("No personality set!")
            return None

        # Prepare context from source tweets
        context = self._prepare_context(source_tweets)

        # Get system prompt
        system_prompt = self.current_personality.get('system_prompt', '')

        # Create user prompt
        user_prompt = f"""
İşte kaynak tweet'ler:

{context}

Yukarıdaki tweet'lere dayanarak, kendi tarzınla yeni bir tweet oluştur.
Kurallar:
- Maksimum 280 karakter
- Türkçe olmalı
- Sadece tweet'i yaz, başka açıklama yapma
- Doğrudan tweet metnini ver
"""

        try:
            # Generate with Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            generated_text = response.choices[0].message.content.strip()

            # Clean up response
            generated_text = self._clean_tweet(generated_text)

            self.logger.info(f"Generated tweet: {generated_text[:50]}...")
            return generated_text

        except Exception as e:
            self.logger.error(f"Error generating tweet: {e}")
            return None

    def _prepare_context(self, tweets: List[Dict]) -> str:
        """Prepare context string from tweets"""
        context_parts = []

        for i, tweet in enumerate(tweets[:5], 1):  # Max 5 tweets for context
            author = tweet.get('author', 'Unknown')
            text = tweet.get('text', tweet.get('content', ''))
            context_parts.append(f"{i}. @{author}: {text}")

        return "\n\n".join(context_parts)

    def _clean_tweet(self, text: str) -> str:
        """Clean and format generated tweet"""
        # Remove common AI prefixes
        prefixes_to_remove = [
            "İşte tweet:",
            "Tweet:",
            "İşte bir tweet:",
            "Oluşturulan tweet:",
            "Here's the tweet:",
            "Here is the tweet:",
        ]

        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()

        # Remove quotes if the entire text is quoted
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]

        # Ensure it's not too long
        if len(text) > 280:
            text = text[:277] + "..."

        return text.strip()

    def generate_multiple_options(self, source_tweets: List[Dict],
                                  count: int = 3, personality: str = None) -> List[str]:
        """
        Generate multiple tweet options

        Args:
            source_tweets: Source tweets
            count: Number of options to generate
            personality: Personality to use

        Returns:
            List of generated tweet options
        """
        options = []

        for i in range(count):
            tweet = self.generate_tweet(source_tweets, personality)
            if tweet:
                options.append(tweet)

        return options

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text (positive, negative, neutral)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir duygu analizi asistanısın. Verilen metni analiz et ve sadece 'pozitif', 'negatif' veya 'nötr' kelimelerinden birini döndür."
                    },
                    {
                        "role": "user",
                        "content": f"Bu metnin duygusal tonunu belirle: {text}"
                    }
                ],
                temperature=0.3,
                max_tokens=10
            )

            sentiment = response.choices[0].message.content.strip().lower()
            return sentiment

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return "nötr"
