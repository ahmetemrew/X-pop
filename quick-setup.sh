#!/bin/bash

# X-Pop Bot - Quick Setup for Selenium Mode
# Hızlı kurulum: Sadece Twitter kullanıcı adı/şifre ve Groq API key

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}║          🚀  QUICK SETUP - SELENIUM MODE  🚀      ║${NC}"
echo -e "${CYAN}║                                                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# .env dosyası var mı kontrol et
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env dosyası zaten mevcut!${NC}"
    read -p "Üzerine yazılsın mı? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}İptal edildi. Mevcut .env korundu.${NC}"
        exit 0
    fi
fi

echo -e "${CYAN}Bilgileri gir (her birini Enter'la onayla):${NC}"
echo ""

# Twitter bilgileri
echo -e "${YELLOW}📱 TWITTER BİLGİLERİ${NC}"
read -p "Twitter kullanıcı adı (@ olmadan): " TWITTER_USER
read -p "Twitter şifre: " -s TWITTER_PASS
echo ""
read -p "Twitter e-mail (doğrulama için, opsiyonel): " TWITTER_MAIL
echo ""

# Groq API
echo -e "${YELLOW}🤖 GROQ AI API KEY${NC}"
echo -e "${CYAN}Groq API key almak için: https://console.groq.com/keys${NC}"
read -p "Groq API Key: " GROQ_KEY
echo ""

# Headless mode
echo -e "${YELLOW}🖥️  TARAYICI AYARI${NC}"
read -p "Chrome görünmez modda çalışsın mı? (y/n, önerilen: y): " -n 1 -r HEADLESS_CHOICE
echo ""
if [[ $HEADLESS_CHOICE =~ ^[Yy]$ ]]; then
    HEADLESS="true"
else
    HEADLESS="false"
fi

echo ""
echo -e "${CYAN}[1/3] .env dosyası oluşturuluyor...${NC}"

# .env dosyasını oluştur
cat > .env << EOF
# ============================================
# Selenium Mode Configuration
# ============================================

# Twitter Login (Selenium Mode)
TWITTER_USERNAME=${TWITTER_USER}
TWITTER_PASSWORD=${TWITTER_PASS}
TWITTER_EMAIL=${TWITTER_MAIL}

# Selenium Settings
SELENIUM_HEADLESS=${HEADLESS}

# ============================================
# AI Settings
# ============================================

# Groq AI API
GROQ_API_KEY=${GROQ_KEY}

# ============================================
# Twitter API (Not needed for Selenium mode)
# ============================================
# These are only needed if you switch to "api" mode
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=
TWITTER_BEARER_TOKEN=
EOF

echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
echo ""

# Config mode kontrolü
echo -e "${CYAN}[2/3] Config kontrol ediliyor...${NC}"

# Config'de mode selenium olmalı
if grep -q 'mode: "api"' config/config.yaml; then
    echo -e "${YELLOW}⚠️  Config'de mode 'api' olarak ayarlı, 'selenium'a çevriliyor...${NC}"
    sed -i 's/mode: "api"/mode: "selenium"/' config/config.yaml
    echo -e "${GREEN}✅ Mode 'selenium'a çevrildi${NC}"
else
    echo -e "${GREEN}✅ Mode zaten 'selenium'${NC}"
fi
echo ""

# Test
echo -e "${CYAN}[3/3] Kurulum test ediliyor...${NC}"

# Virtual environment var mı?
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment bulunamadı!${NC}"
    echo -e "${YELLOW}Önce ./install.sh çalıştırın${NC}"
    exit 1
fi

# Python test
source venv/bin/activate

python3 << 'PYEOF'
import os
from dotenv import load_dotenv

load_dotenv()

# Gerekli değerleri kontrol et
errors = []

username = os.getenv('TWITTER_USERNAME')
password = os.getenv('TWITTER_PASSWORD')
groq_key = os.getenv('GROQ_API_KEY')

if not username:
    errors.append("TWITTER_USERNAME eksik")
elif username == "your_twitter_username":
    errors.append("TWITTER_USERNAME placeholder değerinde, gerçek değer gir")

if not password:
    errors.append("TWITTER_PASSWORD eksik")
elif password == "your_twitter_password":
    errors.append("TWITTER_PASSWORD placeholder değerinde, gerçek değer gir")

if not groq_key:
    errors.append("GROQ_API_KEY eksik")
elif groq_key == "your_groq_api_key_here":
    errors.append("GROQ_API_KEY placeholder değerinde, gerçek değer gir")

if errors:
    print("\n❌ HATALAR:")
    for err in errors:
        print(f"  - {err}")
    exit(1)
else:
    print("✅ Tüm gerekli değerler mevcut")
    print(f"  - Twitter User: {username}")
    print(f"  - Groq API Key: {groq_key[:10]}...")
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                   ║${NC}"
    echo -e "${GREEN}║         ✅  KURULUM TAMAMLANDI!  ✅              ║${NC}"
    echo -e "${GREEN}║                                                   ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Şimdi ne yapmalısın?${NC}"
    echo ""
    echo -e "${YELLOW}1. Test et (opsiyonel):${NC}"
    echo "   ./test-bot.sh"
    echo ""
    echo -e "${YELLOW}2. Bot'u başlat:${NC}"
    echo "   sudo systemctl start xpop-bot"
    echo ""
    echo -e "${YELLOW}3. Durumu kontrol et:${NC}"
    echo "   twitter"
    echo "   # veya"
    echo "   journalctl -u xpop-bot -f"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Test başarısız! .env dosyasını kontrol et${NC}"
    exit 1
fi
