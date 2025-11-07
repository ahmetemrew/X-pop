#!/bin/bash

# X-Pop Bot - Canlı Log İzleyici

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║            📺  X-POP BOT CANLI İZLEME                ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║            Çıkmak için: Ctrl+C                       ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "logs/bot.log" ]; then
    echo -e "${YELLOW}⚠️  Log dosyası henüz oluşmamış.${NC}"
    echo -e "${YELLOW}Bot'u başlatın: ./start.sh${NC}\n"
    exit 0
fi

echo -e "${GREEN}📊 Canlı log izleme başladı...${NC}\n"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Canlı log izleme
tail -f logs/bot.log | while read line; do
    # Renklendirme
    if echo "$line" | grep -q "ERROR"; then
        echo -e "\033[0;31m$line\033[0m"  # Kırmızı
    elif echo "$line" | grep -q "WARNING"; then
        echo -e "\033[1;33m$line\033[0m"  # Sarı
    elif echo "$line" | grep -q "✅"; then
        echo -e "\033[0;32m$line\033[0m"  # Yeşil
    elif echo "$line" | grep -q "🤖"; then
        echo -e "\033[0;36m$line\033[0m"  # Cyan
    else
        echo "$line"
    fi
done
