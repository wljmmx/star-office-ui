#!/bin/bash

# Star Office UI - Startup Script

echo "=========================================="
echo "🌟 Star Office UI Server"
echo "=========================================="

# Change to backend directory
cd "$(dirname "$0")"

# Check if database exists
if [ ! -f "../skills/github-collab/github-collab.db" ]; then
    echo "❌ Database not found: ../skills/github-collab/github-collab.db"
    echo "Please initialize the database first."
    exit 1
fi

# Check if frontend exists
if [ ! -f "../frontend/index.html" ]; then
    echo "❌ Frontend not found: ../frontend/index.html"
    echo "Please create the frontend first."
    exit 1
fi

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Start server
echo "🚀 Starting server..."
python3 main.py
