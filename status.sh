#!/bin/bash

# X-Pop Bot - Durum Kontrolü

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║              🔍  X-POP BOT DURUMU                     ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Bot çalışıyor mu kontrol et
echo -e "${BLUE}🤖 Bot Durumu:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Screen session kontrolü
if screen -list | grep -q "xpop"; then
    echo -e "  ${GREEN}✅ Bot çalışıyor (screen session: xpop)${NC}"
    SCREEN_RUNNING=true
else
    echo -e "  ${RED}❌ Bot çalışmıyor (screen session bulunamadı)${NC}"
    SCREEN_RUNNING=false
fi

# Process kontrolü
if pgrep -f "src.main" > /dev/null; then
    PID=$(pgrep -f "src.main")
    echo -e "  ${GREEN}✅ Python process aktif (PID: $PID)${NC}"

    # CPU ve Memory kullanımı
    CPU=$(ps -p $PID -o %cpu= 2>/dev/null | tr -d ' ')
    MEM=$(ps -p $PID -o %mem= 2>/dev/null | tr -d ' ')
    echo -e "  ${BLUE}📊 CPU: ${YELLOW}${CPU}%${NC}, RAM: ${YELLOW}${MEM}%${NC}"

    PROCESS_RUNNING=true
else
    echo -e "  ${YELLOW}⚠️  Python process bulunamadı${NC}"
    PROCESS_RUNNING=false
fi

echo ""

# Config kontrolü
echo -e "${BLUE}⚙️  Konfigürasyon:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "config/config.yaml" ]; then
    echo -e "  ${GREEN}✅ config.yaml mevcut${NC}"

    # Mode'u göster
    MODE=$(grep "^mode:" config/config.yaml | awk '{print $2}' | tr -d '"' 2>/dev/null)
    echo -e "  ${BLUE}🔧 Mod:${NC} ${YELLOW}${MODE}${NC}"

    # Kişiliği göster
    PERSONALITY=$(grep "personality:" config/config.yaml | head -1 | awk '{print $2}' | tr -d '"' 2>/dev/null)
    echo -e "  ${BLUE}🎭 Kişilik:${NC} ${YELLOW}${PERSONALITY}${NC}"

    # Interval'i göster
    INTERVAL=$(grep "check_interval:" config/config.yaml | head -1 | awk '{print $2}' 2>/dev/null)
    echo -e "  ${BLUE}⏰ Kontrol Aralığı:${NC} ${YELLOW}${INTERVAL} dakika${NC}"
else
    echo -e "  ${RED}❌ config.yaml bulunamadı${NC}"
fi

if [ -f ".env" ]; then
    echo -e "  ${GREEN}✅ .env dosyası mevcut${NC}"
else
    echo -e "  ${RED}❌ .env dosyası bulunamadı${NC}"
fi

echo ""

# Log kontrolü
echo -e "${BLUE}📝 Log Durumu:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "logs/bot.log" ]; then
    LOG_SIZE=$(du -h logs/bot.log | cut -f1)
    LOG_LINES=$(wc -l < logs/bot.log)
    echo -e "  ${GREEN}✅ Log dosyası: ${LOG_SIZE} (${LOG_LINES} satır)${NC}"

    # Son log zamanı
    LAST_LOG=$(tail -1 logs/bot.log 2>/dev/null | cut -d' ' -f1,2)
    if [ ! -z "$LAST_LOG" ]; then
        echo -e "  ${BLUE}🕐 Son log:${NC} ${YELLOW}${LAST_LOG}${NC}"
    fi

    # Son 3 satır
    echo -e "\n  ${YELLOW}Son 3 log satırı:${NC}"
    tail -3 logs/bot.log | while read line; do
        echo -e "  ${NC}→ ${line:0:80}${NC}"
    done
else
    echo -e "  ${YELLOW}⚠️  Log dosyası henüz oluşmamış${NC}"
fi

echo ""

# Database kontrolü
echo -e "${BLUE}💾 Database:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "data/tweets.db" ]; then
    DB_SIZE=$(du -h data/tweets.db | cut -f1)
    echo -e "  ${GREEN}✅ Database mevcut: ${DB_SIZE}${NC}"

    # Hızlı istatistik
    TOTAL=$(sqlite3 data/tweets.db "SELECT COUNT(*) FROM posted_tweets;" 2>/dev/null || echo "0")
    TODAY=$(date +%Y-%m-%d)
    TODAY_COUNT=$(sqlite3 data/tweets.db "SELECT COUNT(*) FROM posted_tweets WHERE DATE(posted_at) = '$TODAY';" 2>/dev/null || echo "0")

    echo -e "  ${BLUE}📊 Toplam tweet:${NC} ${YELLOW}${TOTAL}${NC}"
    echo -e "  ${BLUE}📅 Bugün:${NC} ${YELLOW}${TODAY_COUNT}${NC}"
else
    echo -e "  ${YELLOW}⚠️  Database henüz oluşmamış${NC}"
fi

echo ""

# Komutlar
echo -e "${BLUE}🎮 Yararlı Komutlar:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$SCREEN_RUNNING" = true ]; then
    echo -e "  ${GREEN}screen -r xpop${NC}         → Bot ekranına bağlan"
    echo -e "  ${GREEN}./monitor.sh${NC}           → Canlı log izle"
else
    echo -e "  ${GREEN}./start.sh${NC}             → Bot'u başlat"
    echo -e "  ${GREEN}screen -S xpop ./start.sh${NC} → Screen ile başlat"
fi

echo -e "  ${GREEN}./stats.sh${NC}             → Detaylı istatistikler"
echo -e "  ${GREEN}tail -f logs/bot.log${NC}   → Log dosyasını izle"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Durum kontrolü tamamlandı: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""
