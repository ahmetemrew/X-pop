#!/bin/bash

# X-Pop Bot - Systemd Service Otomatik Kurulum
# Bot her zaman arka planda çalışır, SSH kopsa bile

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║        🔧  SYSTEMD SERVICE KURULUM  🔧               ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║    Bot sürekli arka planda çalışacak                 ║${NC}"
echo -e "${CYAN}║    SSH kapansa bile durma yacak!                      ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Bu script'i sudo ile çalıştırmalısınız!${NC}"
    echo -e "${YELLOW}Doğru kullanım: sudo ./service-install.sh${NC}\n"
    exit 1
fi

# Geçerli dizin ve kullanıcı
CURRENT_DIR=$(pwd)
CURRENT_USER=$(logname)

echo -e "${YELLOW}📁 Proje dizini: ${CURRENT_DIR}${NC}"
echo -e "${YELLOW}👤 Kullanıcı: ${CURRENT_USER}${NC}\n"

# Service dosyası oluştur
SERVICE_FILE="/etc/systemd/system/xpop-bot.service"

echo -e "${CYAN}[1/5]${NC} Service dosyası oluşturuluyor...\n"

cat > $SERVICE_FILE << EOF
[Unit]
Description=X-Pop Bot - AI-powered Twitter Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python -m src.main
Restart=always
RestartSec=10
StandardOutput=append:$CURRENT_DIR/logs/bot.log
StandardError=append:$CURRENT_DIR/logs/error.log

# Environment
Environment="PYTHONUNBUFFERED=1"

# Resource limits (opsiyonel)
MemoryLimit=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Service dosyası oluşturuldu: $SERVICE_FILE${NC}\n"

# Systemd'yi reload et
echo -e "${CYAN}[2/5]${NC} Systemd reload ediliyor...\n"
systemctl daemon-reload
echo -e "${GREEN}✅ Systemd reload edildi${NC}\n"

# Servisi enable et (otomatik başlasın)
echo -e "${CYAN}[3/5]${NC} Servis aktif ediliyor (otomatik başlatma)...\n"
systemctl enable xpop-bot
echo -e "${GREEN}✅ Servis aktif edildi${NC}\n"

# Servisi başlat
echo -e "${CYAN}[4/5]${NC} Servis başlatılıyor...\n"
systemctl start xpop-bot
echo -e "${GREEN}✅ Servis başlatıldı${NC}\n"

# Durum kontrolü
echo -e "${CYAN}[5/5]${NC} Servis durumu kontrol ediliyor...\n"
sleep 2

if systemctl is-active --quiet xpop-bot; then
    echo -e "${GREEN}✅ Servis başarıyla çalışıyor!${NC}\n"
else
    echo -e "${RED}❌ Servis başlatılamadı!${NC}"
    echo -e "${YELLOW}Log'ları kontrol edin: sudo journalctl -u xpop-bot -n 50${NC}\n"
    exit 1
fi

# twitter komutu oluştur
echo -e "${CYAN}[BONUS]${NC} 'twitter' komutu oluşturuluyor...\n"

# twitter script'ini /usr/local/bin'e kopyala
if [ -f "$CURRENT_DIR/twitter" ]; then
    cp "$CURRENT_DIR/twitter" /usr/local/bin/twitter
    chmod +x /usr/local/bin/twitter
    echo -e "${GREEN}✅ 'twitter' komutu oluşturuldu${NC}\n"
fi

# Başarı mesajı
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}║           ✅  KURULUM TAMAMLANDI!  ✅                 ║${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}📋 Artık şunları yapabilirsiniz:${NC}\n"

echo -e "  ${YELLOW}1.${NC} Bot'u kontrol edin:"
echo -e "     ${GREEN}twitter${NC}                    → İnteraktif dashboard"
echo -e "     ${GREEN}sudo systemctl status xpop-bot${NC} → Servis durumu\n"

echo -e "  ${YELLOW}2.${NC} Servis yönetimi:"
echo -e "     ${GREEN}sudo systemctl start xpop-bot${NC}  → Başlat"
echo -e "     ${GREEN}sudo systemctl stop xpop-bot${NC}   → Durdur"
echo -e "     ${GREEN}sudo systemctl restart xpop-bot${NC} → Yeniden başlat\n"

echo -e "  ${YELLOW}3.${NC} Log'ları izleyin:"
echo -e "     ${GREEN}sudo journalctl -u xpop-bot -f${NC} → Canlı log\n"

echo -e "${CYAN}💡 İpucu:${NC} Artık SSH'tan çıksan bile bot çalışmaya devam eder!"
echo -e "${CYAN}💡 İpucu:${NC} Sadece ${GREEN}twitter${NC} yazarak durumu görebilirsin!\n"
