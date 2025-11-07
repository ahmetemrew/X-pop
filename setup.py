#!/usr/bin/env python3
"""
X-Pop Bot - Interactive Setup Script
Terminal'den tüm ayarları alır ve otomatik konfigüre eder
"""

import os
import sys
import getpass
from pathlib import Path
import yaml


class Colors:
    """Terminal renkleri"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Setup banner'ını göster"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════╗
║                                                       ║
║          {Colors.YELLOW}🤖  X-POP BOT KURULUM  🤖{Colors.CYAN}                 ║
║                                                       ║
║     {Colors.GREEN}Interaktif Terminal Kurulum Sihirbazı{Colors.CYAN}          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)


def ask(question, default=None, password=False):
    """Kullanıcıdan input al"""
    if default:
        prompt = f"{Colors.BLUE}❓ {question} [{Colors.YELLOW}{default}{Colors.BLUE}]: {Colors.END}"
    else:
        prompt = f"{Colors.BLUE}❓ {question}: {Colors.END}"

    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt).strip()

    return value if value else default


def ask_yes_no(question, default='y'):
    """Evet/Hayır sorusu sor"""
    choices = f"[{Colors.GREEN}E{Colors.END}/h]" if default.lower() == 'e' else f"[e/{Colors.RED}H{Colors.END}]"
    prompt = f"{Colors.BLUE}❓ {question} {choices}: {Colors.END}"

    answer = input(prompt).strip().lower()
    if not answer:
        answer = default.lower()

    return answer in ['e', 'evet', 'y', 'yes']


def print_step(step_num, title):
    """Adım başlığı göster"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}📋 Adım {step_num}: {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_success(message):
    """Başarı mesajı"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    """Hata mesajı"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_info(message):
    """Bilgi mesajı"""
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")


def print_warning(message):
    """Uyarı mesajı"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def setup_twitter_credentials():
    """Twitter hesap bilgilerini al"""
    print_step(1, "Twitter Hesap Bilgileri")

    print_info("Selenium modu kullanılacak - API anahtarı gerekmez!")
    print_info("Twitter hesap bilgilerinizi girin:\n")

    username = ask("Twitter kullanıcı adınız (@ olmadan)")
    while not username:
        print_error("Kullanıcı adı boş olamaz!")
        username = ask("Twitter kullanıcı adınız (@ olmadan)")

    password = ask("Twitter şifreniz", password=True)
    while not password:
        print_error("Şifre boş olamaz!")
        password = ask("Twitter şifreniz", password=True)

    email = ask("Twitter email adresiniz (doğrulama için, opsiyonel)")

    headless = ask_yes_no("Tarayıcı görünmez modda çalışsın mı?", 'e')

    return {
        'username': username,
        'password': password,
        'email': email if email else '',
        'headless': 'true' if headless else 'false'
    }


def setup_monitored_accounts():
    """Takip edilecek hesapları al"""
    print_step(2, "Takip Edilecek Hesaplar")

    print_info("Hangi hesapları takip etmek istiyorsunuz?")
    print_info("Örnek: bbcturkce, cnnturk, NTV\n")

    accounts = []

    print(f"{Colors.CYAN}Hesapları tek tek girin (bitirmek için boş bırakın):{Colors.END}\n")

    while True:
        account = ask(f"Hesap #{len(accounts)+1} (@ olmadan)", default="")
        if not account:
            break
        account = account.lstrip('@').strip()
        if account:
            accounts.append(account)
            print_success(f"Eklendi: @{account}")

    if not accounts:
        print_warning("Hesap eklenmedi, varsayılanlar kullanılacak")
        accounts = ['bbcturkce', 'cnnturk', 'NTV']
        print_info(f"Varsayılan hesaplar: {', '.join(['@'+a for a in accounts])}")

    return accounts


def setup_ai_configuration():
    """AI konfigürasyonu"""
    print_step(3, "Yapay Zeka Ayarları")

    print_info("Ücretsiz AI seçenekleri:\n")
    print(f"  {Colors.GREEN}1.{Colors.END} Groq (Llama 3.1 70B) - {Colors.YELLOW}ÖNERİLEN{Colors.END}")
    print(f"     → Çok hızlı, ücretsiz, mükemmel Türkçe")
    print(f"     → https://console.groq.com/\n")

    # Şimdilik sadece Groq destekleniyor
    print_info("Şu anda sadece Groq desteklenmektedir.")

    api_key = ask("Groq API Key'iniz (console.groq.com'dan alın)")
    while not api_key:
        print_error("API Key boş olamaz!")
        print_info("https://console.groq.com/ adresinden ücretsiz alabilirsiniz")
        api_key = ask("Groq API Key'iniz")

    return {
        'provider': 'groq',
        'api_key': api_key,
        'model': 'llama-3.1-70b-versatile'
    }


def setup_bot_personality():
    """Bot kişiliğini seç"""
    print_step(4, "Bot Kişiliği ve Davranışı")

    print_info("Bot nasıl davranmalı? Kişilik seçin:\n")

    personalities = {
        '1': ('yorumcu', 'Yorumcu - Haberleri yorumlayarak paylaşır'),
        '2': ('haber_duyurucu', 'Haber Duyurucu - Objektif, düz haber'),
        '3': ('analist', 'Analist - Derin analiz ve içgörüler'),
        '4': ('mizahci', 'Mizahçı - Esprili ama saygılı'),
        '5': ('sakin_paylasimci', 'Sakin Paylaşımcı - Minimal, az kelime')
    }

    for key, (name, desc) in personalities.items():
        print(f"  {Colors.GREEN}{key}.{Colors.END} {desc}")

    print()
    choice = ask("Seçiminiz", default='1')

    personality_key, personality_desc = personalities.get(choice, personalities['1'])
    print_success(f"Seçildi: {personality_desc}")

    return personality_key


def setup_schedule():
    """Zamanlama ayarları"""
    print_step(5, "Zamanlama Ayarları")

    print_info("Bot ne sıklıkta kontrol etsin?\n")

    interval = ask("Kontrol aralığı (dakika)", default='10')
    try:
        interval = int(interval)
        if interval < 1:
            interval = 10
    except:
        interval = 10

    print_success(f"Kontrol aralığı: Her {interval} dakikada bir")

    tweets_per_run = ask("Her çalıştırmada kaç tweet atılsın?", default='1')
    try:
        tweets_per_run = int(tweets_per_run)
        if tweets_per_run < 1:
            tweets_per_run = 1
    except:
        tweets_per_run = 1

    print_success(f"Tweet sayısı: Her çalıştırmada {tweets_per_run} tweet")

    return {
        'interval': interval,
        'tweets_per_run': tweets_per_run
    }


def create_env_file(twitter_creds, ai_config, schedule):
    """`.env` dosyası oluştur"""
    print_step(6, ".env Dosyası Oluşturuluyor")

    env_content = f"""# ============================================
# Selenium Mode Configuration
# ============================================
# Twitter Login Credentials
TWITTER_USERNAME={twitter_creds['username']}
TWITTER_PASSWORD={twitter_creds['password']}
TWITTER_EMAIL={twitter_creds['email']}

# Selenium Settings
SELENIUM_HEADLESS={twitter_creds['headless']}

# ============================================
# AI Settings
# ============================================
# Groq AI API (https://console.groq.com/)
GROQ_API_KEY={ai_config['api_key']}

# Bot Settings
CHECK_INTERVAL_MINUTES={schedule['interval']}
MAX_TWEETS_PER_RUN=10
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    # Güvenlik için izinleri ayarla
    os.chmod('.env', 0o600)

    print_success(".env dosyası oluşturuldu")


def create_config_file(accounts, personality, schedule):
    """config.yaml dosyası oluştur"""
    print_info("config/config.yaml dosyası oluşturuluyor...")

    config = {
        'mode': 'selenium',
        'monitored_accounts': accounts,
        'bot': {
            'personality': personality,
            'check_interval': schedule['interval'],
            'max_tweets_per_run': 10,
            'tweets_to_post_per_run': schedule['tweets_per_run'],
            'min_tweet_length': 20
        },
        'ai': {
            'model': 'llama-3.1-70b-versatile',
            'temperature': 0.7,
            'max_tokens': 280
        },
        'duplicate_detection': {
            'enabled': True,
            'similarity_threshold': 0.85,
            'check_last_days': 7
        },
        'debug': {
            'enabled': False,
            'save_raw_tweets': True
        }
    }

    os.makedirs('config', exist_ok=True)

    with open('config/config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print_success("config/config.yaml dosyası oluşturuldu")


def print_summary(twitter_creds, accounts, personality, schedule):
    """Ayarların özetini göster"""
    print_step(7, "Kurulum Özeti")

    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    print(f"\n{Colors.BOLD}Twitter Hesabı:{Colors.END}")
    print(f"  Kullanıcı: @{twitter_creds['username']}")
    print(f"  Headless: {twitter_creds['headless']}")

    print(f"\n{Colors.BOLD}Takip Edilen Hesaplar:{Colors.END}")
    for acc in accounts:
        print(f"  • @{acc}")

    print(f"\n{Colors.BOLD}Bot Ayarları:{Colors.END}")
    print(f"  Kişilik: {personality}")
    print(f"  Kontrol: Her {schedule['interval']} dakikada")
    print(f"  Tweet: {schedule['tweets_per_run']} tweet/çalıştırma")

    print(f"\n{Colors.BOLD}Mod:{Colors.END}")
    print(f"  Selenium Mode (API gerekmez)")

    print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}\n")


def check_dependencies():
    """Bağımlılıkları kontrol et"""
    print_info("Bağımlılıklar kontrol ediliyor...")

    try:
        import selenium
        import yaml
        import dotenv
        print_success("Tüm bağımlılıklar yüklü")
        return True
    except ImportError as e:
        print_error(f"Eksik bağımlılık: {e}")
        print_info("Lütfen önce: pip install -r requirements.txt")
        return False


def main():
    """Ana setup fonksiyonu"""
    print_banner()

    print(f"{Colors.BOLD}Hoş geldiniz! Bu sihirbaz size kurulum konusunda yardımcı olacak.{Colors.END}\n")

    # Bağımlılıkları kontrol et
    if not check_dependencies():
        print_error("Önce bağımlılıkları yükleyin: pip install -r requirements.txt")
        sys.exit(1)

    # .env dosyası zaten varsa uyar
    if os.path.exists('.env'):
        print_warning(".env dosyası zaten mevcut!")
        if not ask_yes_no("Üzerine yazmak istiyor musunuz?", 'h'):
            print_info("Kurulum iptal edildi.")
            sys.exit(0)

    # Adım adım kurulum
    twitter_creds = setup_twitter_credentials()
    accounts = setup_monitored_accounts()
    ai_config = setup_ai_configuration()
    personality = setup_bot_personality()
    schedule = setup_schedule()

    # Dosyaları oluştur
    create_env_file(twitter_creds, ai_config, schedule)
    create_config_file(accounts, personality, schedule)

    # Gerekli klasörleri oluştur
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Özeti göster
    print_summary(twitter_creds, accounts, personality, schedule)

    # Başarı mesajı
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}✅ KURULUM TAMAMLANDI!{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'='*60}{Colors.END}\n")

    print(f"{Colors.YELLOW}Sonraki adımlar:{Colors.END}\n")
    print(f"  {Colors.GREEN}1.{Colors.END} Test edin:")
    print(f"     {Colors.CYAN}python -m src.main --test{Colors.END}\n")

    print(f"  {Colors.GREEN}2.{Colors.END} Dry run yapın (tweet atmadan):")
    print(f"     {Colors.CYAN}python -m src.main --dry-run{Colors.END}\n")

    print(f"  {Colors.GREEN}3.{Colors.END} Başlatın:")
    print(f"     {Colors.CYAN}python -m src.main{Colors.END}\n")

    # Hemen başlat mı?
    if ask_yes_no("Şimdi botu test etmek ister misiniz?", 'e'):
        print(f"\n{Colors.CYAN}Bot test ediliyor...{Colors.END}\n")
        os.system('python -m src.main --test')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Kurulum iptal edildi.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Hata oluştu: {e}{Colors.END}")
        sys.exit(1)
