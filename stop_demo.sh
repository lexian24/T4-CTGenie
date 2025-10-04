#!/bin/bash

# CTGenie Stop Script
# Cleanly stops both backend and frontend servers

echo "⏹  Stopping CTGenie Demo System..."
echo ""

# Kill processes on ports 8000 and 5173
echo "🧹 Stopping Backend (port 8000)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend stopped"
else
    echo "ℹ️  No backend process found"
fi

echo "🧹 Stopping Frontend (port 5173)..."
lsof -ti:5173 | xargs kill -9 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Frontend stopped"
else
    echo "ℹ️  No frontend process found"
fi

echo ""
echo "✅ CTGenie Demo System stopped successfully!"
