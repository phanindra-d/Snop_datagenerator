#!/bin/bash
# SNOP Data Generator - Dependency Installer (Mac/Linux)

set -e  # Exit on error

echo "========================================="
echo "SNOP Data Generator - Installing Dependencies"
echo "========================================="
echo ""

# Check Python version
echo "[1/4] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Install Python 3.9+ first."
    exit 1
fi

# Check pip
echo ""
echo "[2/4] Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found. Install pip first."
    exit 1
fi

# Install Python packages
echo ""
echo "[3/4] Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt

# Check Kaggle API setup
echo ""
echo "[4/4] Checking Kaggle API setup..."
KAGGLE_CONFIG="$HOME/.kaggle/kaggle.json"

if [ -f "$KAGGLE_CONFIG" ]; then
    echo "✓ Kaggle API credentials found at $KAGGLE_CONFIG"

    # Check permissions
    PERMS=$(stat -f "%A" "$KAGGLE_CONFIG" 2>/dev/null || stat -c "%a" "$KAGGLE_CONFIG" 2>/dev/null)
    if [ "$PERMS" != "600" ]; then
        echo "⚠️  WARNING: Kaggle config has incorrect permissions ($PERMS)"
        echo "   Setting permissions to 600..."
        chmod 600 "$KAGGLE_CONFIG"
        echo "   ✓ Fixed"
    fi
else
    echo "⚠️  WARNING: Kaggle API credentials not found"
    echo ""
    echo "   Phase 4 (Historical Data) requires Kaggle API."
    echo "   To set up:"
    echo "   1. Go to https://www.kaggle.com/account"
    echo "   2. Click 'Create New API Token'"
    echo "   3. Move downloaded kaggle.json to: $KAGGLE_CONFIG"
    echo "   4. Run: chmod 600 $KAGGLE_CONFIG"
    echo ""
    echo "   You can skip this if you won't run Phase 4."
fi

echo ""
echo "========================================="
echo "✓ Installation Complete"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env"
echo "  2. Edit .env with your PostgreSQL credentials"
echo "  3. Run: ./run_all_phases.sh"
echo ""
