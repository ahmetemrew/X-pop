#!/bin/bash

# X-Pop Bot - İstatistik Görüntüleyici

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║              📊  X-POP BOT İSTATİSTİKLER              ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Database kontrolü
if [ ! -f "data/tweets.db" ]; then
    echo -e "${YELLOW}⚠️  Database bulunamadı. Bot hiç çalışmamış olabilir.${NC}\n"
    exit 0
fi

# SQLite ile istatistikleri al
echo -e "${BLUE}📈 Genel İstatistikler:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Toplanan tweetler
TOTAL_COLLECTED=$(sqlite3 data/tweets.db "SELECT COUNT(*) FROM collected_tweets;" 2>/dev/null || echo "0")
echo -e "  ${GREEN}📥 Toplanan Tweet:${NC} ${YELLOW}${TOTAL_COLLECTED}${NC}"

# Paylaşılan tweetler
TOTAL_POSTED=$(sqlite3 data/tweets.db "SELECT COUNT(*) FROM posted_tweets;" 2>/dev/null || echo "0")
echo -e "  ${GREEN}📤 Paylaşılan Tweet:${NC} ${YELLOW}${TOTAL_POSTED}${NC}"

# İşlenmemiş tweetler
UNPROCESSED=$(sqlite3 data/tweets.db "SELECT COUNT(*) FROM collected_tweets WHERE processed = 0;" 2>/dev/null || echo "0")
echo -e "  ${GREEN}⏳ İşlenmemiş:${NC} ${YELLOW}${UNPROCESSED}${NC}"

# Bugünkü tweetler
TODAY=$(date +%Y-%m-%d)
TODAY_POSTS=$(sqlite3 data/tweets.db "SELECT COUNT(*) FROM posted_tweets WHERE DATE(posted_at) = '$TODAY';" 2>/dev/null || echo "0")
echo -e "  ${GREEN}📅 Bugün Paylaşılan:${NC} ${YELLOW}${TODAY_POSTS}${NC}"

echo ""
echo -e "${BLUE}⏰ Son Aktiviteler:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Son 5 paylaşılan tweet
echo -e "${MAGENTA}Son 5 Paylaşılan Tweet:${NC}"
sqlite3 -column -header data/tweets.db "
SELECT
    substr(content, 1, 50) || '...' as Tweet,
    personality as Kişilik,
    datetime(posted_at, 'localtime') as Zaman
FROM posted_tweets
ORDER BY posted_at DESC
LIMIT 5;" 2>/dev/null || echo "  Veri yok"

echo ""

# Kişilik dağılımı
echo -e "${BLUE}🎭 Kişilik Dağılımı:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
sqlite3 -column -header data/tweets.db "
SELECT
    personality as Kişilik,
    COUNT(*) as Adet
FROM posted_tweets
GROUP BY personality
ORDER BY COUNT(*) DESC;" 2>/dev/null || echo "  Veri yok"

echo ""

# Son 7 günlük grafik
echo -e "${BLUE}📊 Son 7 Günlük Aktivite:${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
sqlite3 -column -header data/tweets.db "
SELECT
    DATE(posted_at) as Tarih,
    COUNT(*) as 'Tweet Sayısı'
FROM posted_tweets
WHERE DATE(posted_at) >= DATE('now', '-7 days')
GROUP BY DATE(posted_at)
ORDER BY DATE(posted_at) DESC;" 2>/dev/null || echo "  Veri yok"

echo ""

# Disk kullanımı
DB_SIZE=$(du -h data/tweets.db 2>/dev/null | cut -f1)
echo -e "${GREEN}💾 Database Boyutu:${NC} ${YELLOW}${DB_SIZE}${NC}"

# Log dosyası boyutu
if [ -f "logs/bot.log" ]; then
    LOG_SIZE=$(du -h logs/bot.log 2>/dev/null | cut -f1)
    echo -e "${GREEN}📝 Log Dosyası:${NC} ${YELLOW}${LOG_SIZE}${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ İstatistikler güncellendi: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""
