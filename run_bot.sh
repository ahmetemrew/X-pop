#!/bin/bash

# X-Pop Bot Starter Script

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════╗"
echo "║              🤖  X-POP BOT  🤖                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and fill in your API keys${NC}"
    echo ""
    echo "Steps:"
    echo "  1. cp .env.example .env"
    echo "  2. Edit .env and add your API keys"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p logs data

# Run the bot
echo -e "${GREEN}Starting X-Pop Bot...${NC}"
echo ""

python -m src.main "$@"

# Deactivate virtual environment
deactivate
