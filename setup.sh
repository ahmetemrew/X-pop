#!/bin/bash

# X-Pop Bot - Tek Komutla Tam Kurulum
# Bu script her şeyi yapar: kurulum, yapılandırma, başlatma

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                               ║${NC}"
echo -e "${CYAN}║              🚀  X-POP BOT TAM KURULUM  🚀                    ║${NC}"
echo -e "${CYAN}║                                                               ║${NC}"
echo -e "${CYAN}║       Twitter Bot - Tek komutta kurulum ve başlatma          ║${NC}"
echo -e "${CYAN}║                                                               ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Bu script'i root olarak çalıştırmalısınız!${NC}"
    echo -e "${YELLOW}Doğru kullanım: sudo ./setup.sh${NC}\n"
    exit 1
fi

# Kullanıcı belirleme
if [ -z "$SUDO_USER" ]; then
    CURRENT_USER="root"
    USER_HOME="/root"
else
    CURRENT_USER="$SUDO_USER"
    USER_HOME=$(eval echo ~$SUDO_USER)
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}📁 Kurulum dizini: ${SCRIPT_DIR}${NC}"
echo -e "${CYAN}👤 Kullanıcı: ${CURRENT_USER}${NC}"
echo ""
echo -e "${YELLOW}Bu script şunları yapacak:${NC}"
echo -e "  1️⃣  Sistem paketlerini yükle (Python, Chrome, vb)"
echo -e "  2️⃣  Python bağımlılıklarını yükle"
echo -e "  3️⃣  Twitter hesap bilgilerini al"
echo -e "  4️⃣  Bot'u yapılandır"
echo -e "  5️⃣  Systemd servis olarak kur"
echo -e "  6️⃣  Bot'u başlat"
echo ""
read -p "Devam etmek istiyor musunuz? (e/h): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ee]$ ]]; then
    echo -e "${RED}Kurulum iptal edildi.${NC}"
    exit 1
fi

# ==============================================================================
# ADIM 1: SİSTEM PAKETLERİNİ YÜKLE
# ==============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}[1/6] Sistem paketleri yükleniyor...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

apt update -qq
apt install -y -qq python3 python3-pip python3-venv wget curl git > /dev/null 2>&1

# Chrome kurulu değilse kur
if ! command -v google-chrome &> /dev/null; then
    echo -e "${YELLOW}  → Google Chrome yükleniyor...${NC}"
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
    apt install -y -qq /tmp/chrome.deb > /dev/null 2>&1 || true
    rm /tmp/chrome.deb
fi

echo -e "${GREEN}✅ Sistem paketleri yüklendi${NC}"

# ==============================================================================
# ADIM 2: PYTHON BAĞIMLILIKLAR
# ==============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}[2/6] Python bağımlılıkları yükleniyor...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

cd "$SCRIPT_DIR"

# Virtual environment oluştur
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}  → Virtual environment oluşturuluyor...${NC}"
    python3 -m venv venv
fi

# Paketleri yükle
echo -e "${YELLOW}  → Python paketleri yükleniyor...${NC}"
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo -e "${GREEN}✅ Python bağımlılıkları yüklendi${NC}"

# ==============================================================================
# ADIM 3: HESAP BİLGİLERİNİ AL
# ==============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}[3/6] Twitter hesap bilgileri alınıyor...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Kullanıcı bilgilerini sor
read -p "Twitter kullanıcı adınız (@ olmadan): " TWITTER_USERNAME
read -sp "Twitter şifreniz: " TWITTER_PASSWORD
echo ""
read -p "Twitter email'iniz (opsiyonel, Enter ile geç): " TWITTER_EMAIL
echo ""

# Takip edilecek hesaplar
echo ""
echo -e "${YELLOW}Takip edilecek hesapları girin (virgülle ayırın):${NC}"
echo -e "${YELLOW}Örnek: cnnturk, hurriyet, haberturk${NC}"
read -p "Hesaplar: " MONITORED_ACCOUNTS

# Kontrol aralığı
echo ""
read -p "Kontrol aralığı (dakika) [varsayılan: 15]: " CHECK_INTERVAL
CHECK_INTERVAL=${CHECK_INTERVAL:-15}

# Kişilik seç
echo ""
echo -e "${YELLOW}Bot kişiliğini seçin:${NC}"
echo "  1) Yorumcu (detaylı analiz ve yorum)"
echo "  2) Haber Duyurucu (kısa, net haberler)"
echo "  3) Analist (veri odaklı, analitik)"
echo "  4) Mizahçı (eğlenceli, hafif)"
echo "  5) Sakin Paylaşımcı (dengeli, profesyonel)"
read -p "Seçiminiz (1-5) [varsayılan: 5]: " PERSONALITY_CHOICE
PERSONALITY_CHOICE=${PERSONALITY_CHOICE:-5}

case $PERSONALITY_CHOICE in
    1) PERSONALITY="yorumcu" ;;
    2) PERSONALITY="haber_duyurucu" ;;
    3) PERSONALITY="analist" ;;
    4) PERSONALITY="mizahci" ;;
    5) PERSONALITY="sakin_paylasimci" ;;
    *) PERSONALITY="sakin_paylasimci" ;;
esac

# Groq API key
echo ""
echo -e "${YELLOW}Groq API Key (ücretsiz - groq.com'dan alın):${NC}"
read -p "API Key: " GROQ_API_KEY

echo -e "${GREEN}✅ Bilgiler alındı${NC}"

# ==============================================================================
# ADIM 4: YAPILANDIRMA DOSYALARI OLUŞTUR
# ==============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}[4/6] Yapılandırma dosyaları oluşturuluyor...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# .env dosyası oluştur
cat > "$SCRIPT_DIR/.env" << EOF
# Twitter Hesap Bilgileri (Selenium Mode)
TWITTER_USERNAME=$TWITTER_USERNAME
TWITTER_PASSWORD=$TWITTER_PASSWORD
TWITTER_EMAIL=$TWITTER_EMAIL

# AI API
GROQ_API_KEY=$GROQ_API_KEY

# Diğer
LOG_LEVEL=INFO
EOF

# config.yaml oluştur
IFS=',' read -ra ACCOUNTS_ARRAY <<< "$MONITORED_ACCOUNTS"
ACCOUNTS_YAML=""
for account in "${ACCOUNTS_ARRAY[@]}"; do
    account=$(echo "$account" | xargs)  # Trim whitespace
    ACCOUNTS_YAML="${ACCOUNTS_YAML}  - \"${account}\"\n"
done

cat > "$SCRIPT_DIR/config/config.yaml" << EOF
# X-Pop Bot Yapılandırması

# Twitter modu: "selenium" (hesap/şifre) veya "api" (API key)
mode: "selenium"

# Takip edilecek hesaplar
monitored_accounts:
$(echo -e "$ACCOUNTS_YAML")

# Kontrol aralığı (dakika)
check_interval: $CHECK_INTERVAL

# AI Ayarları
ai:
  provider: "groq"
  model: "llama-3.1-70b-versatile"
  personality: "$PERSONALITY"
  max_tokens: 280

# İnsan gibi davranış
human_behavior:
  random_timing:
    enabled: true
    min_extra_minutes: 5
    max_extra_minutes: 20
  working_hours_start: 7
  working_hours_end: 1
  random_skip_chance: 0.05
  typing_speed:
    min_delay: 0.1
    max_delay: 0.3

# Resim ayarları
images:
  enabled: true
  search_engine: "google"
  download_timeout: 10

# Database
database:
  path: "data/bot.db"

# Selenium ayarları
selenium:
  headless: true
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  window_size: "1920,1080"
  timeout: 30
  cookie_file: "data/twitter_cookies.json"
EOF

# Log ve data dizinleri oluştur
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/data"
mkdir -p "$SCRIPT_DIR/downloads"

# Dizin izinlerini düzelt
chown -R $CURRENT_USER:$CURRENT_USER "$SCRIPT_DIR"

echo -e "${GREEN}✅ Yapılandırma tamamlandı${NC}"

# ==============================================================================
# ADIM 5: SYSTEMD SERVİS OLUŞTUR
# ==============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}[5/6] Systemd servisi oluşturuluyor...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Service dosyası oluştur
cat > /etc/systemd/system/xpop-bot.service << EOF
[Unit]
Description=X-Pop Bot - AI-powered Twitter Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/venv/bin/python -m src.main
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/logs/bot.log
StandardError=append:$SCRIPT_DIR/logs/error.log

Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

# Systemd reload
systemctl daemon-reload
systemctl enable xpop-bot

echo -e "${GREEN}✅ Systemd servisi oluşturuldu${NC}"

# ==============================================================================
# ADIM 6: BOT'U BAŞLAT
# ==============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}[6/6] Bot başlatılıyor...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# twitter komutunu kur
if [ -f "$SCRIPT_DIR/twitter" ]; then
    cp "$SCRIPT_DIR/twitter" /usr/local/bin/twitter
    chmod +x /usr/local/bin/twitter
fi

# Servisi başlat
systemctl start xpop-bot
sleep 3

# Durum kontrolü
if systemctl is-active --quiet xpop-bot; then
    echo -e "${GREEN}✅ Bot başarıyla başlatıldı!${NC}"
else
    echo -e "${RED}❌ Bot başlatılamadı. Log'ları kontrol edin:${NC}"
    echo -e "${YELLOW}   journalctl -u xpop-bot -n 50${NC}"
    exit 1
fi

# ==============================================================================
# BAŞARI MESAJI
# ==============================================================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║              ✅  KURULUM TAMAMLANDI!  ✅                      ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📋 Bot başarıyla kuruldu ve çalışıyor!${NC}"
echo ""
echo -e "${YELLOW}Kullanabileceğiniz komutlar:${NC}"
echo ""
echo -e "  ${GREEN}twitter${NC}                      → Bot durumu ve istatistikler"
echo -e "  ${GREEN}./edit-settings.sh${NC}           → Ayarları değiştir"
echo -e "  ${GREEN}systemctl status xpop-bot${NC}   → Servis durumu"
echo -e "  ${GREEN}systemctl restart xpop-bot${NC}  → Bot'u yeniden başlat"
echo -e "  ${GREEN}journalctl -u xpop-bot -f${NC}   → Canlı log izle"
echo ""
echo -e "${CYAN}💡 Bot SSH'tan çıksan bile çalışmaya devam edecek!${NC}"
echo -e "${CYAN}💡 Sadece 'twitter' yazarak durumu görebilirsin!${NC}"
echo ""
