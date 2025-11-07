"""
Image Fetcher - Google'dan görsel bulma ve indirme
"""

import os
import requests
import logging
from typing import Optional, List
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import time


class ImageFetcher:
    def __init__(self, download_dir: str = "data/images"):
        """
        Initialize image fetcher

        Args:
            download_dir: Görsellerin indirileceği klasör
        """
        self.download_dir = download_dir
        self.logger = logging.getLogger(__name__)

        # Klasörü oluştur
        os.makedirs(self.download_dir, exist_ok=True)

        # User agent (Google bot algılamasın)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def search_google_images(self, query: str, num_results: int = 5) -> List[str]:
        """
        Google Images'da arama yap ve görsel URL'lerini al

        Args:
            query: Arama sorgusu
            num_results: Kaç görsel URL'i döndürülsün

        Returns:
            Görsel URL'lerinin listesi
        """
        try:
            # Google Images arama URL'i
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch"

            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # HTML'i parse et
            soup = BeautifulSoup(response.text, 'html.parser')

            # Görsel URL'lerini bul
            image_urls = []

            # img tag'lerinden URL'leri çek
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and src.startswith('http'):
                    image_urls.append(src)
                    if len(image_urls) >= num_results:
                        break

            self.logger.info(f"Found {len(image_urls)} images for query: {query}")
            return image_urls

        except Exception as e:
            self.logger.error(f"Error searching images: {e}")
            return []

    def download_image(self, url: str, filename: str = None) -> Optional[str]:
        """
        Görseli indir

        Args:
            url: Görsel URL'i
            filename: Kaydedilecek dosya adı (opsiyonel)

        Returns:
            İndirilen dosyanın yolu veya None
        """
        try:
            # Filename oluştur
            if not filename:
                filename = f"img_{int(time.time())}.jpg"

            filepath = os.path.join(self.download_dir, filename)

            # Görseli indir
            response = requests.get(url, headers=self.headers, timeout=15, stream=True)
            response.raise_for_status()

            # Dosyaya yaz
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Downloaded image: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            return None

    def fetch_image_for_tweet(self, tweet_content: str) -> Optional[str]:
        """
        Tweet içeriğine göre görsel bul ve indir

        Args:
            tweet_content: Tweet içeriği

        Returns:
            İndirilen görselin yolu veya None
        """
        try:
            # Tweet'ten anahtar kelimeleri çıkar (basit versiyon)
            # Hashtag ve mention'ları temizle
            import re
            clean_content = re.sub(r'[@#]\w+', '', tweet_content)
            clean_content = re.sub(r'http\S+', '', clean_content)
            clean_content = clean_content.strip()

            # İlk 100 karakteri al (çok uzun arama sorgusu olmasın)
            query = clean_content[:100]

            if not query:
                self.logger.warning("Empty query, skipping image fetch")
                return None

            self.logger.info(f"Searching image for: {query[:50]}...")

            # Google'da ara
            image_urls = self.search_google_images(query, num_results=3)

            if not image_urls:
                self.logger.warning("No images found")
                return None

            # İlk görseli indir
            for url in image_urls:
                filepath = self.download_image(url)
                if filepath:
                    return filepath

            return None

        except Exception as e:
            self.logger.error(f"Error fetching image for tweet: {e}")
            return None

    def cleanup_old_images(self, max_age_hours: int = 24):
        """
        Eski görselleri temizle

        Args:
            max_age_hours: Kaç saatten eski görseller silinsin
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            deleted_count = 0

            for filename in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, filename)

                # Dosya yaşını kontrol et
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)

                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        deleted_count += 1

            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old images")

        except Exception as e:
            self.logger.error(f"Error cleaning up images: {e}")


# Alternatif: Unsplash API (daha güvenilir ama rate limited)
class UnsplashImageFetcher:
    """
    Unsplash API ile görsel bulma (alternatif, daha kaliteli)
    Ücretsiz: https://unsplash.com/developers
    """

    def __init__(self, access_key: str = None, download_dir: str = "data/images"):
        self.access_key = access_key
        self.download_dir = download_dir
        self.logger = logging.getLogger(__name__)
        os.makedirs(self.download_dir, exist_ok=True)

    def search_images(self, query: str, per_page: int = 5) -> List[str]:
        """Unsplash'ta görsel ara"""
        if not self.access_key:
            self.logger.warning("No Unsplash access key provided")
            return []

        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': query,
                'per_page': per_page,
                'client_id': self.access_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            # URL'leri çıkar
            image_urls = [r['urls']['regular'] for r in results if 'urls' in r]

            self.logger.info(f"Found {len(image_urls)} Unsplash images for: {query}")
            return image_urls

        except Exception as e:
            self.logger.error(f"Error searching Unsplash: {e}")
            return []

    def download_image(self, url: str, filename: str = None) -> Optional[str]:
        """Unsplash görselini indir"""
        try:
            if not filename:
                filename = f"unsplash_{int(time.time())}.jpg"

            filepath = os.path.join(self.download_dir, filename)

            response = requests.get(url, timeout=15, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Downloaded Unsplash image: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error downloading Unsplash image: {e}")
            return None
