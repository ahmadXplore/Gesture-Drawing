@echo off
echo 🎨 Gesture Drawing Application - Setup Script
echo ==============================================
echo.

echo 📋 Checking Python version...
python --version
echo.

echo 📦 Creating virtual environment...
python -m venv venv
echo.

echo ✅ Activating virtual environment...
call venv\Scripts\activate
echo.

echo 📥 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo.

echo ✅ Setup complete!
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run: python main.py
echo.
echo Happy Drawing! 🎨
pause
