#!/bin/bash

# X-Pop Bot - Kolay Başlatma Scripti

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════╗"
echo "║              🤖  X-POP BOT  🤖                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı!${NC}"
    echo -e "${CYAN}İlk kurulum için setup.py çalıştırılıyor...${NC}"
    echo ""
    python3 setup.py
    exit 0
fi

# Check if config exists
if [ ! -f config/config.yaml ]; then
    echo -e "${RED}❌ config/config.yaml dosyası bulunamadı!${NC}"
    echo -e "${YELLOW}Lütfen setup.py çalıştırın: python3 setup.py${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p logs data

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment oluşturuluyor...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Virtual environment aktif ediliyor...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${GREEN}Bağımlılıklar kontrol ediliyor...${NC}"
pip install -q -r requirements.txt

# Run the bot
echo -e "${GREEN}Bot başlatılıyor...${NC}"
echo ""

python -m src.main "$@"

# Deactivate virtual environment
deactivate
