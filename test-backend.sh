#!/bin/bash

echo "🧪 Testing AG-UI POC Backend..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if backend is running
echo "Test 1: Checking if backend is accessible..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is NOT running${NC}"
    echo "   Please start the backend first:"
    echo "   → ./start-backend.sh"
    exit 1
fi

echo ""

# Test 2: Health check
echo "Test 2: Checking Ollama connection..."
response=$(curl -s http://localhost:8000/health)
if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Ollama is connected${NC}"
    echo "   Available models:"
    echo "$response" | jq -r '.available_models[]' 2>/dev/null || echo "$response"
else
    echo -e "${RED}❌ Ollama is NOT accessible${NC}"
    echo "   Response: $response"
    echo ""
    echo "   Please check:"
    echo "   1. Ollama is running: ollama serve"
    echo "   2. Model is installed: ollama pull mistral:latest"
    exit 1
fi

echo ""

# Test 3: Send a test chat message
echo "Test 3: Sending test message to /chat endpoint..."
echo "   Message: 'Say hello in one word'"
echo ""

response=$(curl -s -N http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Say hello in one word"}
    ],
    "model": "mistral:latest"
  }')

if [ -z "$response" ]; then
    echo -e "${RED}❌ No response received${NC}"
    echo "   Check backend terminal for error logs"
else
    echo -e "${GREEN}✅ Response received${NC}"
    echo ""
    echo "Response preview (first 500 chars):"
    echo "---"
    echo "$response" | head -c 500
    echo ""
    echo "---"
    
    # Count events
    event_count=$(echo "$response" | grep -c "data:")
    echo ""
    echo "   Total events received: $event_count"
fi

echo ""
echo "🎯 Test complete!"
echo ""
echo "Next steps:"
echo "1. Check the backend terminal for detailed logs"
echo "2. Look for lines starting with 🌐, 🤖, 🔵, 📤, etc."
echo "3. If you see errors, they will be marked with ❌"
