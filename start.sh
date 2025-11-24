#!/bin/bash

# CyberGuard Academy Startup Script
# This script helps you quickly start the application

set -e

echo "🛡️  CyberGuard Academy Startup"
echo "================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your GOOGLE_API_KEY"
    echo "   Get your free API key from: https://aistudio.google.com/app/apikey"
    echo ""
    echo "   After adding your API key, run this script again."
    exit 1
fi

# Check if GOOGLE_API_KEY is set
if ! grep -q "GOOGLE_API_KEY=.*[a-zA-Z0-9]" .env; then
    echo "⚠️  GOOGLE_API_KEY not configured in .env"
    echo ""
    echo "   Please edit .env and add your API key:"
    echo "   GOOGLE_API_KEY=your_api_key_here"
    echo ""
    echo "   Get your free API key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down CyberGuard Academy..."
    kill $API_PID 2>/dev/null || true
    kill $UI_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Activate virtual environment if it exists
if [ -d .venv ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

# Kill any existing processes on ports 8000 and 8501
echo "🧹 Cleaning up any existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
sleep 1

# Start API server
echo "🚀 Starting API Server..."
python api.py > api.log 2>&1 &
API_PID=$!

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API Server is ready!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ API Server failed to start. Check api.log for details."
        cat api.log
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""

# Start Streamlit UI
echo "🎨 Starting Streamlit UI..."
STREAMLIT_SERVER_HEADLESS=true streamlit run ui.py --server.headless true > ui.log 2>&1 &
UI_PID=$!

echo ""
echo "✅ CyberGuard Academy is running!"
echo ""
echo "📊 Access the application:"
echo "   - Web UI: http://localhost:8501"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   - API: tail -f api.log"
echo "   - UI: tail -f ui.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait
