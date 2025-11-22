#!/bin/bash
# X-Pop Bot Health Check & Monitoring Script

echo "🏥 X-Pop Bot Health Check"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if service is installed
if ! systemctl list-unit-files | grep -q "xpop-bot.service"; then
    echo -e "${YELLOW}⚠️  Service not installed${NC}"
    echo "Run: sudo ./install-service.sh"
    echo ""
    echo "Or run manually: python3 -m src.main"
    exit 1
fi

# Check service status
echo -e "${CYAN}📊 Service Status:${NC}"
echo "-----------------------------------"

if systemctl is-active --quiet xpop-bot; then
    echo -e "${GREEN}✅ Service is RUNNING${NC}"
    STATUS="running"
else
    echo -e "${RED}❌ Service is STOPPED${NC}"
    STATUS="stopped"
fi

if systemctl is-enabled --quiet xpop-bot; then
    echo -e "${GREEN}✅ Service is ENABLED (auto-start on boot)${NC}"
else
    echo -e "${YELLOW}⚠️  Service is DISABLED (won't start on boot)${NC}"
fi

echo ""

# Show uptime if running
if [ "$STATUS" = "running" ]; then
    echo -e "${CYAN}⏱️  Uptime:${NC}"
    echo "-----------------------------------"
    systemctl show xpop-bot --property=ActiveEnterTimestamp --value
    echo ""
    
    # Show restart count
    RESTART_COUNT=$(systemctl show xpop-bot --property=NRestarts --value)
    echo -e "${CYAN}🔄 Restart Count: ${YELLOW}$RESTART_COUNT${NC}"
    if [ "$RESTART_COUNT" -gt 10 ]; then
        echo -e "${RED}⚠️  High restart count - check logs for errors${NC}"
    fi
    echo ""
fi

# Show recent logs
echo -e "${CYAN}📋 Recent Logs (last 20 lines):${NC}"
echo "-----------------------------------"
journalctl -u xpop-bot -n 20 --no-pager | tail -20
echo ""

# Check for errors in logs
echo -e "${CYAN}⚠️  Recent Errors:${NC}"
echo "-----------------------------------"
ERROR_COUNT=$(journalctl -u xpop-bot --since "1 hour ago" | grep -i "error\|critical\|fatal" | wc -l)

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No errors in last hour${NC}"
else
    echo -e "${YELLOW}⚠️  Found $ERROR_COUNT error(s) in last hour${NC}"
    echo ""
    echo "Recent errors:"
    journalctl -u xpop-bot --since "1 hour ago" | grep -i "error\|critical\|fatal" | tail -5
fi

echo ""

# Check database
echo -e "${CYAN}💾 Database Status:${NC}"
echo "-----------------------------------"
if [ -f "data/xpop.db" ]; then
    DB_SIZE=$(du -h data/xpop.db | awk '{print $1}')
    echo -e "${GREEN}✅ Database exists: $DB_SIZE${NC}"
else
    echo -e "${YELLOW}⚠️  Database not found (may not have run yet)${NC}"
fi

echo ""

# Check log files
echo -e "${CYAN}📄 Log Files:${NC}"
echo "-----------------------------------"
if [ -d "/var/log/xpop-bot" ]; then
    STDOUT_SIZE=$(du -h /var/log/xpop-bot/stdout.log 2>/dev/null | awk '{print $1}' || echo "0K")
    STDERR_SIZE=$(du -h /var/log/xpop-bot/stderr.log 2>/dev/null | awk '{print $1}' || echo "0K")
    echo -e "stdout.log: $STDOUT_SIZE"
    echo -e "stderr.log: $STDERR_SIZE"
    
    # Check if logs are too large
    STDOUT_KB=$(du -k /var/log/xpop-bot/stdout.log 2>/dev/null | awk '{print $1}' || echo "0")
    if [ "$STDOUT_KB" -gt 102400 ]; then  # 100MB
        echo -e "${YELLOW}⚠️  Log files are large (>100MB), consider rotating${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Log directory not found${NC}"
fi

echo ""

# Show available commands
echo "========================================"
echo -e "${CYAN}💡 Quick Commands:${NC}"
echo "========================================"
echo "• View live logs:    sudo journalctl -u xpop-bot -f"
echo "• Restart service:   sudo systemctl restart xpop-bot"
echo "• Stop service:      sudo systemctl stop xpop-bot"
echo "• Start service:     sudo systemctl start xpop-bot"
echo "• Full status:       sudo systemctl status xpop-bot"
echo ""
echo "• View last 100 logs: sudo journalctl -u xpop-bot -n 100"
echo "• View errors only:   sudo journalctl -u xpop-bot | grep -i error"
echo "• Clear old logs:     sudo journalctl --vacuum-time=7d"
echo ""

# Overall health score
echo "========================================"
if [ "$STATUS" = "running" ] && [ "$ERROR_COUNT" -lt 5 ]; then
    echo -e "${GREEN}🛡️  Overall Health: GOOD${NC}"
elif [ "$STATUS" = "running" ]; then
    echo -e "${YELLOW}🛡️  Overall Health: OK (some errors)${NC}"
else
    echo -e "${RED}🛡️  Overall Health: STOPPED${NC}"
fi
echo "========================================"
echo ""
