#!/bin/bash

# X-Pop Bot - Quick Test Script
# Hızlı test için kullan

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}║           🧪  BOT TEST SCRIPT  🧪                ║${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment bulunamadı!${NC}"
    echo -e "${YELLOW}Önce ./setup.sh veya ./install.sh çalıştırın${NC}\n"
    exit 1
fi

source venv/bin/activate

echo -e "${CYAN}[1/5] Python paketleri kontrol ediliyor...${NC}"

python3 << 'PYEOF'
import sys

errors = []

try:
    import groq
    print(f"✓ groq {groq.__version__}")
except Exception as e:
    errors.append(f"groq: {e}")

try:
    import tweepy
    print(f"✓ tweepy")
except Exception as e:
    errors.append(f"tweepy: {e}")

try:
    import selenium
    print(f"✓ selenium")
except Exception as e:
    errors.append(f"selenium: {e}")

try:
    import yaml
    print(f"✓ pyyaml")
except Exception as e:
    errors.append(f"pyyaml: {e}")

if errors:
    print("\n❌ PAKET HATALARI:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("\n✅ Tüm paketler yüklü")
PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Paket kontrolü başarısız${NC}\n"
    exit 1
fi

echo ""
echo -e "${CYAN}[2/5] Config dosyaları kontrol ediliyor...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env dosyası bulunamadı${NC}"
    exit 1
fi

if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}❌ config.yaml bulunamadı${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .env mevcut${NC}"
echo -e "${GREEN}✓ config.yaml mevcut${NC}"

# Config içeriğini kontrol et
python3 << 'PYEOF'
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

# .env kontrol
groq_key = os.getenv('GROQ_API_KEY')
twitter_user = os.getenv('TWITTER_USERNAME')
twitter_pass = os.getenv('TWITTER_PASSWORD')

if not groq_key:
    print("❌ GROQ_API_KEY eksik")
    exit(1)
else:
    print(f"✓ GROQ_API_KEY: {groq_key[:10]}...")

if not twitter_user:
    print("❌ TWITTER_USERNAME eksik")
    exit(1)
else:
    print(f"✓ TWITTER_USERNAME: {twitter_user}")

if not twitter_pass:
    print("❌ TWITTER_PASSWORD eksik")
    exit(1)
else:
    print("✓ TWITTER_PASSWORD: ****")

# Config kontrol
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

required_keys = ['mode', 'monitored_accounts', 'bot', 'ai']

for key in required_keys:
    if key not in config:
        print(f"❌ config.yaml eksik key: {key}")
        exit(1)

print(f"✓ Config mode: {config['mode']}")
print(f"✓ Monitored accounts: {len(config.get('monitored_accounts', []))}")

PYEOF

if [ $? -ne 0 ]; then
    echo -e "\n${RED}Config kontrolü başarısız${NC}\n"
    exit 1
fi

echo ""
echo -e "${CYAN}[3/5] Dizinler kontrol ediliyor...${NC}"

for dir in logs data downloads; do
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}  Oluşturuluyor: $dir${NC}"
        mkdir -p "$dir"
    fi
    echo -e "${GREEN}✓ $dir/${NC}"
done

echo ""
echo -e "${CYAN}[4/5] AI Generator test ediliyor...${NC}"

python3 << 'PYEOF'
import os
from dotenv import load_dotenv
from src.ai_generator import AIGenerator

load_dotenv()

try:
    api_key = os.getenv('GROQ_API_KEY')
    ai = AIGenerator(
        api_key=api_key,
        model="llama-3.1-70b-versatile",
        temperature=0.7,
        max_tokens=280
    )
    print("✅ AI Generator başarıyla initialize edildi")

    # Personality test
    ai.set_personality("haber_duyurucu")
    print("✅ Personality ayarlandı")

except Exception as e:
    print(f"❌ AI Generator hatası: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}AI Generator testi başarısız${NC}\n"
    exit 1
fi

echo ""
echo -e "${CYAN}[5/5] Database test ediliyor...${NC}"

python3 << 'PYEOF'
from src.database import Database

try:
    db = Database()
    stats = db.get_statistics()
    print(f"✅ Database bağlantısı başarılı")
    print(f"  - Toplam collected: {stats['total_collected']}")
    print(f"  - Toplam posted: {stats['total_posted']}")
except Exception as e:
    print(f"❌ Database hatası: {e}")
    exit(1)

PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Database testi başarısız${NC}\n"
    exit 1
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}║         ✅  TÜM TESTLER BAŞARILI!  ✅            ║${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Bot'u başlatmak için:${NC}"
echo "  • sudo systemctl start xpop-bot"
echo "  • twitter"
echo ""
