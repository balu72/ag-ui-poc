#!/bin/bash

echo "🚀 Starting AG-UI POC Frontend..."
echo ""

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Start the development server
echo ""
echo "✅ Starting Vite dev server..."
echo "   Frontend: http://localhost:5173"
echo ""
npm run dev
