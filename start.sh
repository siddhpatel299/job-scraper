#!/bin/bash
cd "/Users/siddh/Masters/Job Scraper"

echo "🛡️  Cybersecurity Job Scraper - Full Featured"
echo "============================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   venv/bin/pip install -r requirements.txt"
    exit 1
fi

echo "🚀 Starting web interface..."
echo "   The system will automatically find an available port"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the web application with dynamic port
venv/bin/python3 web_app.py
