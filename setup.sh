#!/bin/bash

echo "🎨 Gesture Drawing Application - Setup Script"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python --version

echo ""
echo "📦 Creating virtual environment..."
python -m venv venv

echo ""
echo "✅ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment:"
echo "   Windows (Git Bash): source venv/Scripts/activate"
echo "   Linux/Mac: source venv/bin/activate"
echo "2. Run: python main.py"
echo ""
echo "Happy Drawing! 🎨"
