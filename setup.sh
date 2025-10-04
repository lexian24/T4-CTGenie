#!/bin/bash

# CTGenie First-Time Setup Script
# Run this once to install all dependencies

echo "🏥 CTGenie - Initial Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
echo "1️⃣  Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Found: Python $PYTHON_VERSION"

# Check Node.js version
echo ""
echo "2️⃣  Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "   Found: Node $NODE_VERSION"

# Create Python virtual environment
echo ""
echo "3️⃣  Creating Python virtual environment..."
if [ -d "ctgenie_venv" ]; then
    echo "   ⚠️  Virtual environment already exists, skipping..."
else
    python3 -m venv ctgenie_venv
    echo "   ✅ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo ""
echo "4️⃣  Installing Python dependencies..."
source ctgenie_venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r ctgenie/backend/requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✅ Python dependencies installed"
else
    echo "   ❌ Failed to install Python dependencies"
    exit 1
fi

# Install Node.js dependencies
echo ""
echo "5️⃣  Installing Node.js dependencies..."
cd ctgenie/frontend
if [ -d "node_modules" ]; then
    echo "   ⚠️  node_modules already exists, skipping..."
else
    npm install
    if [ $? -eq 0 ]; then
        echo "   ✅ Node.js dependencies installed"
    else
        echo "   ❌ Failed to install Node.js dependencies"
        exit 1
    fi
fi
cd ../..

# Create logs directory
echo ""
echo "6️⃣  Creating logs directory..."
mkdir -p logs
echo "   ✅ Logs directory created"

# Verify installation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Installation Summary:"
echo "   Python: $PYTHON_VERSION"
echo "   Node.js: $NODE_VERSION"
echo "   Virtual Environment: ✅"
echo "   Backend Dependencies: ✅"
echo "   Frontend Dependencies: ✅"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   To start the demo system:"
echo "   ./start_demo.sh"
echo ""
echo "   Or manually:"
echo "   Terminal 1: source ctgenie_venv/bin/activate && cd ctgenie/backend && python main.py"
echo "   Terminal 2: cd ctgenie/frontend && npm run dev"
echo ""
echo "   Then open: http://localhost:5173"
echo ""
echo "📖 Documentation:"
echo "   README.md       - Full installation and usage guide"
echo "   DEMO_GUIDE.md   - Presentation script and tips"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
