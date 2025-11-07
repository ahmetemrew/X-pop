#!/bin/bash

# X-Pop Bot - Ayarları Düzenle
# Kurulumdan sonra ayarları değiştirmek için

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clear
echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║           ⚙️   AYARLARI DÜZENLE   ⚙️                  ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Mevcut ayarları göster
echo -e "${YELLOW}Mevcut Ayarlar:${NC}"
echo ""

# .env dosyasından oku
if [ -f "$SCRIPT_DIR/.env" ]; then
    CURRENT_USERNAME=$(grep TWITTER_USERNAME "$SCRIPT_DIR/.env" | cut -d '=' -f2)
    CURRENT_EMAIL=$(grep TWITTER_EMAIL "$SCRIPT_DIR/.env" | cut -d '=' -f2)
    echo -e "  Twitter Kullanıcı: ${GREEN}$CURRENT_USERNAME${NC}"
    echo -e "  Twitter Email: ${GREEN}$CURRENT_EMAIL${NC}"
fi

# config.yaml'dan oku
if [ -f "$SCRIPT_DIR/config/config.yaml" ]; then
    CURRENT_INTERVAL=$(grep "check_interval:" "$SCRIPT_DIR/config/config.yaml" | awk '{print $2}')
    CURRENT_PERSONALITY=$(grep "personality:" "$SCRIPT_DIR/config/config.yaml" | awk '{print $2}' | tr -d '"')
    echo -e "  Kontrol Aralığı: ${GREEN}$CURRENT_INTERVAL dakika${NC}"
    echo -e "  Kişilik: ${GREEN}$CURRENT_PERSONALITY${NC}"
fi

echo ""
echo -e "${YELLOW}Neyi değiştirmek istiyorsunuz?${NC}"
echo ""
echo "  1) Twitter hesap bilgileri (kullanıcı adı, şifre)"
echo "  2) Takip edilen hesaplar"
echo "  3) Kontrol aralığı"
echo "  4) Bot kişiliği"
echo "  5) Groq API key"
echo "  6) Resim özelliğini aç/kapat"
echo "  0) İptal"
echo ""

read -p "Seçiminiz (0-6): " choice

case $choice in
    1)
        echo ""
        echo -e "${CYAN}Twitter Hesap Bilgilerini Güncelle${NC}"
        read -p "Yeni kullanıcı adı (@ olmadan): " NEW_USERNAME
        read -sp "Yeni şifre: " NEW_PASSWORD
        echo ""
        read -p "Yeni email: " NEW_EMAIL

        sed -i "s/^TWITTER_USERNAME=.*/TWITTER_USERNAME=$NEW_USERNAME/" "$SCRIPT_DIR/.env"
        sed -i "s/^TWITTER_PASSWORD=.*/TWITTER_PASSWORD=$NEW_PASSWORD/" "$SCRIPT_DIR/.env"
        sed -i "s/^TWITTER_EMAIL=.*/TWITTER_EMAIL=$NEW_EMAIL/" "$SCRIPT_DIR/.env"

        # Cookie dosyasını sil (yeniden giriş yapması için)
        rm -f "$SCRIPT_DIR/data/twitter_cookies.json"

        echo -e "${GREEN}✅ Twitter hesap bilgileri güncellendi${NC}"
        ;;

    2)
        echo ""
        echo -e "${CYAN}Takip Edilen Hesapları Güncelle${NC}"
        echo -e "${YELLOW}Mevcut hesaplar:${NC}"
        grep -A 100 "monitored_accounts:" "$SCRIPT_DIR/config/config.yaml" | grep "^  -" | sed 's/  - /  - /'
        echo ""
        echo -e "${YELLOW}Yeni hesap listesi (virgülle ayırın):${NC}"
        read -p "Hesaplar: " NEW_ACCOUNTS

        # YAML formatında yeniden oluştur
        IFS=',' read -ra ACCOUNTS_ARRAY <<< "$NEW_ACCOUNTS"
        TEMP_FILE=$(mktemp)

        # monitored_accounts satırına kadar kopyala
        sed '/^monitored_accounts:/q' "$SCRIPT_DIR/config/config.yaml" > "$TEMP_FILE"

        # Yeni hesapları ekle
        for account in "${ACCOUNTS_ARRAY[@]}"; do
            account=$(echo "$account" | xargs)
            echo "  - \"$account\"" >> "$TEMP_FILE"
        done

        # Geri kalan kısmı ekle (monitored_accounts sonrası)
        sed -n '/^monitored_accounts:/,/^[a-z]/p' "$SCRIPT_DIR/config/config.yaml" | tail -n +2 | grep -v "^  -" >> "$TEMP_FILE" 2>/dev/null || true
        sed -n '/^check_interval:/,$p' "$SCRIPT_DIR/config/config.yaml" >> "$TEMP_FILE"

        mv "$TEMP_FILE" "$SCRIPT_DIR/config/config.yaml"

        echo -e "${GREEN}✅ Takip edilen hesaplar güncellendi${NC}"
        ;;

    3)
        echo ""
        echo -e "${CYAN}Kontrol Aralığını Güncelle${NC}"
        read -p "Yeni kontrol aralığı (dakika): " NEW_INTERVAL

        sed -i "s/^check_interval:.*/check_interval: $NEW_INTERVAL/" "$SCRIPT_DIR/config/config.yaml"

        echo -e "${GREEN}✅ Kontrol aralığı güncellendi: $NEW_INTERVAL dakika${NC}"
        ;;

    4)
        echo ""
        echo -e "${CYAN}Bot Kişiliğini Güncelle${NC}"
        echo "  1) Yorumcu"
        echo "  2) Haber Duyurucu"
        echo "  3) Analist"
        echo "  4) Mizahçı"
        echo "  5) Sakin Paylaşımcı"
        read -p "Seçiminiz (1-5): " PERS_CHOICE

        case $PERS_CHOICE in
            1) NEW_PERSONALITY="yorumcu" ;;
            2) NEW_PERSONALITY="haber_duyurucu" ;;
            3) NEW_PERSONALITY="analist" ;;
            4) NEW_PERSONALITY="mizahci" ;;
            5) NEW_PERSONALITY="sakin_paylasimci" ;;
            *) echo -e "${RED}Geçersiz seçim${NC}"; exit 1 ;;
        esac

        sed -i "s/personality:.*/personality: \"$NEW_PERSONALITY\"/" "$SCRIPT_DIR/config/config.yaml"

        echo -e "${GREEN}✅ Bot kişiliği güncellendi: $NEW_PERSONALITY${NC}"
        ;;

    5)
        echo ""
        echo -e "${CYAN}Groq API Key Güncelle${NC}"
        read -p "Yeni API key: " NEW_API_KEY

        sed -i "s/^GROQ_API_KEY=.*/GROQ_API_KEY=$NEW_API_KEY/" "$SCRIPT_DIR/.env"

        echo -e "${GREEN}✅ Groq API key güncellendi${NC}"
        ;;

    6)
        echo ""
        echo -e "${CYAN}Resim Özelliği${NC}"
        read -p "Resimleri aktif et? (e/h): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Ee]$ ]]; then
            sed -i "s/enabled: false/enabled: true/" "$SCRIPT_DIR/config/config.yaml"
            echo -e "${GREEN}✅ Resim özelliği aktif edildi${NC}"
        else
            sed -i "s/enabled: true/enabled: false/" "$SCRIPT_DIR/config/config.yaml"
            echo -e "${GREEN}✅ Resim özelliği deaktif edildi${NC}"
        fi
        ;;

    0)
        echo -e "${YELLOW}İptal edildi${NC}"
        exit 0
        ;;

    *)
        echo -e "${RED}Geçersiz seçim${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}Bot'u yeniden başlatmak istiyor musunuz?${NC}"
read -p "(Değişikliklerin geçerli olması için gerekli) (e/h): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ee]$ ]]; then
    if [ "$EUID" -eq 0 ]; then
        systemctl restart xpop-bot
    else
        sudo systemctl restart xpop-bot
    fi
    echo -e "${GREEN}✅ Bot yeniden başlatıldı${NC}"

    sleep 2

    if systemctl is-active --quiet xpop-bot 2>/dev/null; then
        echo -e "${GREEN}✅ Bot çalışıyor${NC}"
    else
        echo -e "${RED}❌ Bot başlatılamadı. Log kontrol edin: journalctl -u xpop-bot -n 50${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Değişiklikler kaydedildi ama bot yeniden başlatılmadı.${NC}"
    echo -e "${YELLOW}   Manuel başlatmak için: sudo systemctl restart xpop-bot${NC}"
fi

echo ""
