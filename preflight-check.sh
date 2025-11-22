#!/bin/bash
# X-Pop Bot Pre-Flight Check - Verify all dependencies before starting

echo "🛡️  X-Pop Bot Pre-Flight Check"
echo "========================================"
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# 1. Check Python version
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        check_pass "Python $PYTHON_VERSION installed"
    else
        check_fail "Python 3.8+ required, found $PYTHON_VERSION"
    fi
else
    check_fail "Python 3 not found"
fi

# 2. Check pip
echo ""
echo "📦 Checking pip..."
if command -v pip3 &> /dev/null; then
    check_pass "pip3 installed"
else
    check_fail "pip3 not found"
fi

# 3. Check virtual environment
echo ""
echo "🌐 Checking virtual environment..."
if [ -d "venv" ]; then
    check_pass "venv directory exists"
    
    if [ -f "venv/bin/python3" ]; then
        check_pass "Python installed in venv"
    else
        check_warn "Python not found in venv, may need to recreate"
    fi
else
    check_warn "venv directory not found - will be created automatically"
fi

# 4. Check .env file
echo ""
echo "🔐 Checking .env file..."
if [ -f ".env" ]; then
    check_pass ".env file exists"
    
    # Check required env vars
    if grep -q "TWITTER_USERNAME=" .env && grep -q "GROQ_API_KEY=" .env; then
        check_pass "Required environment variables present"
    else
        check_fail "Missing required environment variables in .env"
    fi
else
    check_fail ".env file not found - run setup.py first"
fi

# 5. Check config file
echo ""
echo "⚙️  Checking config file..."
if [ -f "config/config.yaml" ]; then
    check_pass "config.yaml exists"
else
    check_fail "config/config.yaml not found - run setup.py first"
fi

# 6. Check Chrome/Chromium
echo ""
echo "🌐 Checking Chrome/Chromium..."
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}')
    check_pass "Google Chrome installed: $CHROME_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROMIUM_VERSION=$(chromium-browser --version | awk '{print $2}')
    check_pass "Chromium installed: $CHROMIUM_VERSION"
elif command -v chromium &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version | awk '{print $2}')
    check_pass "Chromium installed: $CHROMIUM_VERSION"
else
    check_warn "Chrome/Chromium not found - Selenium may not work"
    echo "    Install: sudo apt install chromium-browser"
fi

# 7. Check ChromeDriver
echo ""
echo "🚗 Checking ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version | awk '{print $2}')
    check_pass "ChromeDriver installed: $CHROMEDRIVER_VERSION"
else
    check_warn "ChromeDriver not in PATH - bot will try to auto-download"
    echo "    Install manually: sudo apt install chromium-chromedriver"
fi

# 8. Check Python dependencies
echo ""
echo "📚 Checking Python dependencies..."
if [ -f "venv/bin/python3" ]; then
    VENV_PYTHON="venv/bin/python3"
else
    VENV_PYTHON="python3"
fi

# Check key packages
PACKAGES=("selenium" "groq" "python-dotenv" "pyyaml" "colorama")
for pkg in "${PACKAGES[@]}"; do
    if $VENV_PYTHON -c "import $pkg" 2>/dev/null; then
        check_pass "$pkg installed"
    else
        check_warn "$pkg not installed - run: pip install -r requirements.txt"
    fi
done

# 9. Check directories
echo ""
echo "📁 Checking directories..."
for dir in "logs" "data" "config"; do
    if [ -d "$dir" ]; then
        check_pass "$dir/ directory exists"
    else
        check_warn "$dir/ directory missing - will be created automatically"
    fi
done

# 10. Check disk space
echo ""
echo "💾 Checking disk space..."
AVAILABLE=$(df . | awk 'NR==2 {print $4}')
if [ "$AVAILABLE" -gt 1048576 ]; then  # 1GB in KB
    check_pass "Sufficient disk space available"
else
    check_warn "Low disk space (less than 1GB free)"
fi

# 11. Check internet connectivity
echo ""
echo "🌐 Checking internet connectivity..."
if ping -c 1 google.com &> /dev/null; then
    check_pass "Internet connection available"
else
    check_warn "No internet connection - bot may not work properly"
fi

# Summary
echo ""
echo "========================================"
echo "📊 Pre-Flight Check Summary"
echo "========================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Bot is ready to run.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warnings (bot should work but may have issues)${NC}"
    echo ""
    echo "To fix warnings, run:"
    echo "  • Setup: python3 setup.py"
    echo "  • Install deps: pip install -r requirements.txt"
    echo "  • Create venv: python3 -m venv venv"
    exit 0
else
    echo -e "${RED}❌ $ERRORS errors, $WARNINGS warnings${NC}"
    echo ""
    echo "Critical issues found! Fix these first:"
    echo "  1. Run: python3 setup.py"
    echo "  2. Install dependencies: pip install -r requirements.txt"
    echo "  3. Install Chrome: sudo apt install chromium-browser"
    exit 1
fi
