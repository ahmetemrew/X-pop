#!/bin/bash
# X-Pop Bot Service Installer - BULLETPROOF MODE

set -e

echo "🛡️  X-Pop Bot Service Installer - BULLETPROOF MODE"
echo "=================================================="
echo ""

# Get current user and directory
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "📂 Working directory: $CURRENT_DIR"
echo "👤 Running as user: $CURRENT_USER"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script must be run as root (use sudo)"
    echo "Example: sudo ./install-service.sh"
    exit 1
fi

# Create log directory
echo "📁 Creating log directory..."
mkdir -p /var/log/xpop-bot
chown $SUDO_USER:$SUDO_USER /var/log/xpop-bot
chmod 755 /var/log/xpop-bot
echo "✅ Log directory created"

# Replace placeholders in service file
echo "📝 Configuring service file..."
sed -e "s|%USER%|$SUDO_USER|g" \
    -e "s|%WORKDIR%|$CURRENT_DIR|g" \
    xpop-bot.service > /tmp/xpop-bot.service

# Install service file
echo "⚙️  Installing service file..."
cp /tmp/xpop-bot.service /etc/systemd/system/xpop-bot.service
chmod 644 /etc/systemd/system/xpop-bot.service

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable service
echo "✅ Enabling service..."
systemctl enable xpop-bot.service

echo ""
echo "=============================================="
echo "✅ Service installed successfully!"
echo "=============================================="
echo ""
echo "📋 Available commands:"
echo "  • Start:   sudo systemctl start xpop-bot"
echo "  • Stop:    sudo systemctl stop xpop-bot"
echo "  • Restart: sudo systemctl restart xpop-bot"
echo "  • Status:  sudo systemctl status xpop-bot"
echo "  • Logs:    sudo journalctl -u xpop-bot -f"
echo ""
echo "🛡️  BULLETPROOF FEATURES:"
echo "  • Auto-restart on crash (always)"
echo "  • No restart limits"
echo "  • Infinite retry on errors"
echo "  • Full logging to /var/log/xpop-bot/"
echo ""
echo "💡 To start the bot now:"
echo "   sudo systemctl start xpop-bot"
echo ""
