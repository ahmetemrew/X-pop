#!/bin/bash

# X-Pop Bot - Comprehensive Fix Script
# Bu script TÜM sorunları tek seferde çözer

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}║          🔧  KAPSAMLI FİX SCRIPT  🔧             ║${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Bu script'i root olarak çalıştırın!${NC}"
    echo -e "${YELLOW}Kullanım: sudo ./fix-all.sh${NC}\n"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}Bu script şunları yapacak:${NC}"
echo "  1️⃣  Bot'u durduracak"
echo "  2️⃣  Tüm Python paketlerini güncelleyecek"
echo "  3️⃣  Config dosyalarını kontrol edecek"
echo "  4️⃣  Hataları düzeltecek"
echo "  5️⃣  Test edecek"
echo "  6️⃣  Bot'u başlatacak"
echo ""

# Bot'u durdur
echo -e "${CYAN}[1/6] Bot durduruluyor...${NC}"
systemctl stop xpop-bot 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Bot durduruldu${NC}\n"

# Paketleri güncelle
echo -e "${CYAN}[2/6] Python paketleri güncelleniyor...${NC}"
source venv/bin/activate

# Eski groq'u kaldır ve yenisini yükle
pip uninstall -y groq 2>/dev/null || true
pip install --upgrade pip setuptools wheel
pip install groq>=0.11.0
pip install --upgrade tweepy APScheduler sqlalchemy pyyaml python-dotenv selenium webdriver-manager requests colorama beautifulsoup4

echo -e "${GREEN}✅ Paketler güncellendi${NC}"
pip show groq | grep Version
echo ""

# Config kontrolü
echo -e "${CYAN}[3/6] Config dosyaları kontrol ediliyor...${NC}"

# .env kontrolü
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env dosyası bulunamadı!${NC}"
    exit 1
fi

# config.yaml kontrolü ve düzeltme
if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}❌ config.yaml bulunamadı!${NC}"
    exit 1
fi

# config.yaml'ın tüm gerekli alanları olduğundan emin ol
python3 << 'PYEOF'
import yaml
import sys

try:
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Gerekli alanları kontrol et ve ekle
    changed = False

    # AI section
    if 'ai' not in config:
        config['ai'] = {}
        changed = True

    if 'temperature' not in config['ai']:
        config['ai']['temperature'] = 0.7
        changed = True
        print("✓ temperature eklendi")

    if 'provider' not in config['ai']:
        config['ai']['provider'] = 'groq'
        changed = True
        print("✓ provider eklendi")

    if 'model' not in config['ai']:
        config['ai']['model'] = 'llama-3.1-70b-versatile'
        changed = True
        print("✓ model eklendi")

    if 'max_tokens' not in config['ai']:
        config['ai']['max_tokens'] = 280
        changed = True
        print("✓ max_tokens eklendi")

    # Duplicate detection
    if 'duplicate_detection' not in config:
        config['duplicate_detection'] = {
            'enabled': True,
            'similarity_threshold': 0.85,
            'check_last_days': 7
        }
        changed = True
        print("✓ duplicate_detection eklendi")

    # Bot settings
    if 'bot' not in config:
        config['bot'] = {}
        changed = True

    if 'check_interval' not in config['bot']:
        config['bot']['check_interval'] = config.get('check_interval', 5)
        changed = True
        print("✓ bot.check_interval eklendi")

    if 'personality' not in config['bot']:
        config['bot']['personality'] = config.get('ai', {}).get('personality', 'haber_duyurucu')
        changed = True
        print("✓ bot.personality eklendi")

    # Database
    if 'database' not in config:
        config['database'] = {'path': 'data/bot.db'}
        changed = True
        print("✓ database eklendi")

    # Selenium
    if 'selenium' not in config:
        config['selenium'] = {
            'headless': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'window_size': '1920,1080',
            'timeout': 30,
            'cookie_file': 'data/twitter_cookies.json'
        }
        changed = True
        print("✓ selenium eklendi")

    # Human behavior
    if 'human_behavior' not in config:
        config['human_behavior'] = {
            'random_timing': {
                'enabled': True,
                'min_extra_minutes': 5,
                'max_extra_minutes': 20
            },
            'working_hours_start': 7,
            'working_hours_end': 1,
            'random_skip_chance': 0.05
        }
        changed = True
        print("✓ human_behavior eklendi")

    # Images
    if 'images' not in config:
        config['images'] = {'enabled': True}
        changed = True
        print("✓ images eklendi")

    # Kaydet
    if changed:
        with open('config/config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print("\n✅ Config güncellendi")
    else:
        print("✅ Config tamam")

except Exception as e:
    print(f"❌ Config hatası: {e}")
    sys.exit(1)
PYEOF

echo -e "${GREEN}✅ Config kontrol edildi${NC}\n"

# Dizinleri oluştur
echo -e "${CYAN}[4/6] Dizinler kontrol ediliyor...${NC}"
mkdir -p logs data downloads
chmod 755 logs data downloads
echo -e "${GREEN}✅ Dizinler tamam${NC}\n"

# Test et
echo -e "${CYAN}[5/6] Sistem test ediliyor...${NC}"

# Python import testleri
python3 << 'PYEOF'
import sys

print("Python paketleri test ediliyor...")
errors = []

try:
    import groq
    print(f"✓ groq {groq.__version__}")
except Exception as e:
    errors.append(f"groq: {e}")

try:
    import tweepy
    print(f"✓ tweepy {tweepy.__version__}")
except Exception as e:
    errors.append(f"tweepy: {e}")

try:
    import selenium
    print(f"✓ selenium {selenium.__version__}")
except Exception as e:
    errors.append(f"selenium: {e}")

try:
    from webdriver_manager.chrome import ChromeDriverManager
    print("✓ webdriver_manager")
except Exception as e:
    errors.append(f"webdriver_manager: {e}")

try:
    import yaml
    print("✓ pyyaml")
except Exception as e:
    errors.append(f"pyyaml: {e}")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv")
except Exception as e:
    errors.append(f"python-dotenv: {e}")

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    print("✓ APScheduler")
except Exception as e:
    errors.append(f"APScheduler: {e}")

try:
    from sqlalchemy import create_engine
    print("✓ sqlalchemy")
except Exception as e:
    errors.append(f"sqlalchemy: {e}")

if errors:
    print("\n❌ HATALAR:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("\n✅ Tüm paketler yüklü")
PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Test başarısız${NC}\n"
    exit 1
fi

echo -e "${GREEN}✅ Test başarılı${NC}\n"

# Bot'u başlat
echo -e "${CYAN}[6/6] Bot başlatılıyor...${NC}"
systemctl daemon-reload
systemctl start xpop-bot
sleep 3

# Durum kontrolü
if systemctl is-active --quiet xpop-bot; then
    echo -e "${GREEN}✅ Bot başarıyla başlatıldı!${NC}\n"

    echo -e "${CYAN}Son loglar:${NC}"
    journalctl -u xpop-bot -n 20 --no-pager

    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                   ║${NC}"
    echo -e "${GREEN}║              ✅  FİX TAMAMLANDI!  ✅             ║${NC}"
    echo -e "${GREEN}║                                                   ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Şimdi şunları yapabilirsin:${NC}"
    echo "  • twitter           → Bot kontrol paneli"
    echo "  • journalctl -u xpop-bot -f  → Canlı log"
    echo ""
else
    echo -e "${RED}❌ Bot başlatılamadı!${NC}\n"
    echo -e "${YELLOW}Log kontrol et:${NC}"
    journalctl -u xpop-bot -n 50 --no-pager
    echo ""
    exit 1
fi
