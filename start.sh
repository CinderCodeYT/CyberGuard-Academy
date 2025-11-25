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
    echo "⚠️  IMPORTANT: Please edit .env and configure your AI provider"
    echo ""
    echo "   For Groq (Recommended - Free):"
    echo "   1. Get API key from: https://console.groq.com/"
    echo "   2. Set: AI_PROVIDER=groq"
    echo "   3. Set: GROQ_API_KEY=your_key_here"
    echo ""
    echo "   After configuration, run this script again."
    exit 1
fi

# Check if AI provider is configured
AI_PROVIDER=$(grep -E "^AI_PROVIDER=" .env | cut -d'=' -f2 | tr -d ' "' || echo "")

if [ -z "$AI_PROVIDER" ]; then
    echo "⚠️  AI_PROVIDER not set in .env"
    echo ""
    echo "   Please edit .env and set:"
    echo "   AI_PROVIDER=groq  (recommended)"
    echo ""
    exit 1
fi

# Check if API key is configured based on provider
if [ "$AI_PROVIDER" = "groq" ]; then
    if ! grep -q "GROQ_API_KEY=.*[a-zA-Z0-9]" .env; then
        echo "⚠️  GROQ_API_KEY not configured in .env"
        echo ""
        echo "   Please edit .env and add your Groq API key:"
        echo "   GROQ_API_KEY=gsk_your_key_here"
        echo ""
        echo "   Get your free API key from: https://console.groq.com/"
        exit 1
    fi
elif [ "$AI_PROVIDER" = "vertex" ]; then
    if ! grep -q "GOOGLE_CLOUD_PROJECT=.*[a-zA-Z0-9]" .env; then
        echo "⚠️  GOOGLE_CLOUD_PROJECT not configured in .env"
        echo ""
        echo "   Please edit .env and add your GCP project ID"
        echo "   GOOGLE_CLOUD_PROJECT=your-project-id"
        exit 1
    fi
else
    echo "⚠️  Invalid AI_PROVIDER: $AI_PROVIDER"
    echo "   Must be 'groq' or 'vertex'"
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
uvicorn api:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
API_PID=$!

# Wait for API to be ready
echo "⏳ Waiting for API to be ready (initializing agents)..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API Server is ready!"
        break
    fi
    
    # Show progress every 3 seconds
    if [ $((i % 3)) -eq 0 ]; then
        echo "   Still initializing... (${i}s elapsed)"
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ API Server failed to start within 30 seconds. Check api.log for details."
        echo ""
        echo "Last 30 lines of api.log:"
        tail -30 api.log
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
