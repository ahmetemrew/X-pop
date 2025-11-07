"""
Human Behavior Simulator - Bot'u daha insan gibi yap
"""

import random
import time
import logging
from datetime import datetime, time as dt_time
from typing import Tuple


class HumanBehavior:
    """İnsan davranışlarını simüle eder"""

    def __init__(self, config: dict = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        # Çalışma saatleri (varsayılan: 07:00 - 01:00)
        self.working_hours_start = self.config.get('working_hours_start', 7)  # 07:00
        self.working_hours_end = self.config.get('working_hours_end', 1)    # 01:00 (gece)

        # Rastgele davranış ayarları
        self.random_skip_chance = self.config.get('random_skip_chance', 0.05)  # %5
        self.typing_speed_range = self.config.get('typing_speed_range', (0.05, 0.15))  # saniye/karakter

    def calculate_random_interval(self, base_interval: int,
                                  min_extra: int = 5,
                                  max_extra: int = 20) -> int:
        """
        Rastgele interval hesapla

        Args:
            base_interval: Temel interval (dakika)
            min_extra: Minimum ekstra süre (dakika)
            max_extra: Maksimum ekstra süre (dakika)

        Returns:
            Toplam interval (dakika)
        """
        extra = random.randint(min_extra, max_extra)
        total = base_interval + extra

        self.logger.info(f"⏱️  Interval: {base_interval} + {extra} (random) = {total} dakika")

        return total

    def should_skip_this_run(self) -> bool:
        """
        Bu çalıştırmayı rastgele atla mı? (İnsan gibi bazen tweet atmamak)

        Returns:
            True ise bu çalıştırmayı atla
        """
        skip = random.random() < self.random_skip_chance

        if skip:
            self.logger.info("🎲 Random skip - Bu çalıştırmayı atlıyoruz (insan gibi)")

        return skip

    def is_working_hours(self) -> bool:
        """
        Şu an çalışma saatleri içinde mi?

        Returns:
            True ise çalışma saatleri içinde
        """
        now = datetime.now()
        current_hour = now.hour

        # Gece yarısını geçen durumu handle et
        if self.working_hours_start < self.working_hours_end:
            # Normal: 7-23 gibi
            is_working = self.working_hours_start <= current_hour < self.working_hours_end
        else:
            # Gece geçen: 7-1 (gece) gibi
            is_working = current_hour >= self.working_hours_start or current_hour < self.working_hours_end

        if not is_working:
            self.logger.info(f"😴 Çalışma saatleri dışında (şimdi: {current_hour:02d}:00)")

        return is_working

    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 5.0):
        """
        Rastgele gecikme (insan gibi düşünme/okuma süresi)

        Args:
            min_seconds: Minimum gecikme
            max_seconds: Maksimum gecikme
        """
        delay = random.uniform(min_seconds, max_seconds)
        self.logger.debug(f"⏳ Random delay: {delay:.2f} saniye")
        time.sleep(delay)

    def typing_simulation(self, text_length: int) -> float:
        """
        Yazma simülasyonu - insan yazma hızında gecikme

        Args:
            text_length: Metin uzunluğu (karakter)

        Returns:
            Gecikme süresi (saniye)
        """
        # Karakter başına rastgele süre
        per_char_delay = random.uniform(*self.typing_speed_range)
        total_delay = text_length * per_char_delay

        # Minimum 2, maksimum 30 saniye
        total_delay = max(2.0, min(30.0, total_delay))

        self.logger.debug(f"⌨️  Typing simulation: {total_delay:.2f}s for {text_length} chars")

        return total_delay

    def should_add_emoji(self, base_chance: float = 0.7) -> bool:
        """
        Emoji eklensin mi? (Rastgele)

        Args:
            base_chance: Temel ihtimal (0.7 = %70)

        Returns:
            True ise emoji ekle
        """
        return random.random() < base_chance

    def random_emoji_count(self, max_count: int = 3) -> int:
        """
        Rastgele emoji sayısı

        Args:
            max_count: Maksimum emoji sayısı

        Returns:
            Emoji sayısı (0 ile max_count arası)
        """
        # Daha az emoji daha olası
        weights = [0.3, 0.4, 0.2, 0.1][:max_count + 1]
        return random.choices(range(max_count + 1), weights=weights)[0]

    def random_hashtag_count(self, max_count: int = 3) -> int:
        """
        Rastgele hashtag sayısı

        Args:
            max_count: Maksimum hashtag sayısı

        Returns:
            Hashtag sayısı
        """
        # 1-2 hashtag en olası
        if max_count >= 3:
            weights = [0.1, 0.4, 0.4, 0.1]
        elif max_count == 2:
            weights = [0.2, 0.5, 0.3]
        else:
            weights = [0.3, 0.7]

        return random.choices(range(max_count + 1), weights=weights)[0]

    def add_human_variance_to_text(self, text: str) -> str:
        """
        Metne insan varyasyonu ekle (bazen küçük değişiklikler)

        Args:
            text: Orijinal metin

        Returns:
            Değiştirilmiş metin
        """
        # %90 ihtimalle değiştirme (çoğu zaman olduğu gibi)
        if random.random() < 0.9:
            return text

        # Bazı varyasyonlar
        variations = []

        # Nokta ekle/çıkar
        if text.endswith('.'):
            variations.append(text[:-1])
        else:
            variations.append(text + '.')

        # Ünlem ekle
        if not text.endswith('!'):
            variations.append(text + '!')

        # Üç nokta ekle
        variations.append(text + '...')

        # Birini rastgele seç
        modified = random.choice(variations)

        # Hala 280 karakter altındaysa kullan
        if len(modified) <= 280:
            self.logger.debug(f"✏️  Text variation applied")
            return modified

        return text

    def wait_until_working_hours(self):
        """
        Çalışma saatleri başlayana kadar bekle
        """
        while not self.is_working_hours():
            now = datetime.now()
            current_hour = now.hour

            # Çalışma saatine kaç saat var?
            if self.working_hours_start > current_hour:
                hours_until = self.working_hours_start - current_hour
            else:
                hours_until = (24 - current_hour) + self.working_hours_start

            self.logger.info(f"😴 Çalışma saatleri dışında. {hours_until} saat sonra tekrar başlayacak.")

            # 30 dakika bekle ve tekrar kontrol et
            time.sleep(30 * 60)

    def simulate_reading_time(self, tweet_count: int) -> float:
        """
        Tweet okuma süresi simülasyonu

        Args:
            tweet_count: Okunacak tweet sayısı

        Returns:
            Okuma süresi (saniye)
        """
        # Tweet başına 2-5 saniye
        per_tweet = random.uniform(2, 5)
        total = tweet_count * per_tweet

        self.logger.debug(f"📖 Reading simulation: {total:.1f}s for {tweet_count} tweets")

        return total

    def get_random_action_delays(self) -> dict:
        """
        Farklı aksiyonlar için rastgele gecikmeler

        Returns:
            Aksiyon -> gecikme süresi dictionary'si
        """
        return {
            'before_collect': random.uniform(1, 3),
            'after_collect': random.uniform(2, 5),
            'before_generate': random.uniform(1, 4),
            'after_generate': random.uniform(2, 6),
            'before_post': random.uniform(3, 8),
            'after_post': random.uniform(5, 15)
        }


class SmartScheduler:
    """
    Akıllı zamanlayıcı - insan gibi değişken interval'ler
    """

    def __init__(self, base_interval: int = 10):
        """
        Args:
            base_interval: Temel interval (dakika)
        """
        self.base_interval = base_interval
        self.logger = logging.getLogger(__name__)

    def get_next_interval(self, min_extra: int = 5, max_extra: int = 20) -> int:
        """
        Sonraki interval'i hesapla (rastgele eklemeli)

        Args:
            min_extra: Minimum ekstra dakika
            max_extra: Maksimum ekstra dakika

        Returns:
            Sonraki interval (dakika)
        """
        extra = random.randint(min_extra, max_extra)
        next_interval = self.base_interval + extra

        self.logger.info(f"📅 Next check in: {next_interval} minutes (base: {self.base_interval} + random: {extra})")

        return next_interval

    def calculate_wait_time(self, interval_minutes: int) -> Tuple[int, str]:
        """
        Bekleme süresini hesapla ve formatla

        Args:
            interval_minutes: Interval (dakika)

        Returns:
            (saniye, formatlanmış string)
        """
        seconds = interval_minutes * 60

        # Formatlama
        if interval_minutes < 60:
            formatted = f"{interval_minutes} dakika"
        else:
            hours = interval_minutes // 60
            mins = interval_minutes % 60
            formatted = f"{hours} saat {mins} dakika"

        return seconds, formatted
