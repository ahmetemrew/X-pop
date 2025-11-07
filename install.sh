#!/bin/bash

# X-Pop Bot - Ubuntu Sunucu için Otomatik Kurulum
# Python yoksa kurar, tüm bağımlılıkları hazırlar

set -e  # Hata durumunda dur

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║     🚀  X-POP BOT - UBUNTU KURULUM  🚀               ║
║                                                       ║
║     Python yoksa kurar, her şeyi hazırlar            ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Bu scripti root olarak çalıştırmayın!${NC}"
    echo -e "${YELLOW}Normal kullanıcı ile çalıştırın: ./install.sh${NC}\n"
    exit 1
fi

echo -e "${BLUE}[1/6]${NC} Sistem güncellemesi yapılıyor...\n"
sudo apt update -qq

# Python kontrolü
echo -e "${BLUE}[2/6]${NC} Python kontrol ediliyor...\n"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python bulunamadı, kuruluyor...${NC}"
    sudo apt install -y python3 python3-pip python3-venv
    echo -e "${GREEN}✅ Python kuruldu!${NC}\n"
else
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python mevcut: $PYTHON_VERSION${NC}\n"
fi

# Chrome kontrolü (Selenium için)
echo -e "${BLUE}[3/6]${NC} Google Chrome kontrol ediliyor...\n"
if ! command -v google-chrome &> /dev/null; then
    echo -e "${YELLOW}⚠️  Chrome bulunamadı, kuruluyor...${NC}"

    # Chrome'u indir ve kur
    cd /tmp
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y ./google-chrome-stable_current_amd64.deb
    rm google-chrome-stable_current_amd64.deb
    cd - > /dev/null

    echo -e "${GREEN}✅ Chrome kuruldu!${NC}\n"
else
    CHROME_VERSION=$(google-chrome --version)
    echo -e "${GREEN}✅ Chrome mevcut: $CHROME_VERSION${NC}\n"
fi

# Gerekli sistem paketleri
echo -e "${BLUE}[4/6]${NC} Gerekli sistem paketleri kuruluyor...\n"
sudo apt install -y \
    wget \
    curl \
    git \
    screen \
    sqlite3 \
    > /dev/null 2>&1

echo -e "${GREEN}✅ Sistem paketleri kuruldu!${NC}\n"

# Virtual environment oluştur
echo -e "${BLUE}[5/6]${NC} Python virtual environment oluşturuluyor...\n"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment oluşturuldu!${NC}\n"
else
    echo -e "${GREEN}✅ Virtual environment zaten mevcut!${NC}\n"
fi

# Activate ve bağımlılıkları yükle
source venv/bin/activate

echo -e "${BLUE}[6/6]${NC} Python bağımlılıkları yükleniyor...\n"
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo -e "${GREEN}✅ Tüm bağımlılıklar yüklendi!${NC}\n"

# Gerekli klasörleri oluştur
mkdir -p data logs config

# Scriptleri executable yap
chmod +x setup.py start.sh stats.sh status.sh monitor.sh 2>/dev/null || true

deactivate

# Başarı mesajı
echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║                                                       ║${NC}"
echo -e "${GREEN}${BOLD}║          ✅  KURULUM TAMAMLANDI!  ✅                  ║${NC}"
echo -e "${GREEN}${BOLD}║                                                       ║${NC}"
echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}📋 Sonraki adımlar:${NC}\n"
echo -e "  ${YELLOW}1.${NC} Bot'u yapılandırın:"
echo -e "     ${GREEN}python3 setup.py${NC}\n"

echo -e "  ${YELLOW}2.${NC} Bot'u başlatın (screen ile):"
echo -e "     ${GREEN}screen -S xpop${NC}"
echo -e "     ${GREEN}./start.sh${NC}"
echo -e "     ${GREEN}Ctrl+A+D ile çıkın${NC}\n"

echo -e "  ${YELLOW}3.${NC} İstatistikleri görün:"
echo -e "     ${GREEN}./stats.sh${NC}\n"

echo -e "  ${YELLOW}4.${NC} Bot durumunu kontrol edin:"
echo -e "     ${GREEN}./status.sh${NC}\n"

echo -e "  ${YELLOW}5.${NC} Canlı log izleyin:"
echo -e "     ${GREEN}./monitor.sh${NC}\n"

echo -e "${CYAN}💡 İpucu:${NC} Screen'e tekrar bağlanmak için: ${GREEN}screen -r xpop${NC}\n"
