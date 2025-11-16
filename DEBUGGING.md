# 🔍 Debugging Guide for AG-UI POC

This guide helps you troubleshoot and understand the logging in your AG-UI POC application.

## Quick Testing

Run the test script to verify everything is working:
```bash
./test-backend.sh
```

This will:
1. Check if backend is running
2. Verify Ollama connection
3. Send a test message
4. Show you the response

## Understanding Backend Logs

When the backend is running, you'll see detailed logs in the terminal. Here's what each emoji means:

### 🌐 HTTP Endpoints
- `🌐 [CHAT]` - Direct `/chat` endpoint received a request
- `🤖 [COPILOTKIT]` - CopilotKit endpoint `/v1/copilotkit` received a request

### 🔵 Streaming Process
- `🔵 [STREAM]` - Stream initialization
- `🔵 [OLLAMA]` - Communication with Ollama

### 📤 Event Emission
- `📤 [EVENT]` - AG-UI protocol events being sent to frontend
  - START event - Agent starting
  - TEXT_MESSAGE events - Streaming chunks
  - RESULT event - Complete response
  - END event - Agent finished

### 🟢 Success
- `🟢 [OLLAMA]` - Ollama stream started successfully

### 📝 Data Flow
- `📝 [CHUNK]` - Individual chunks from Ollama
- `📨` - Individual messages in the conversation

### ✅ Completion
- `✅ [STREAM]` - Stream completed successfully

### ❌ Errors
- `❌ [ERROR]` - Something went wrong
- `❌ [CHAT]` or `❌ [COPILOTKIT]` - Endpoint error

## Common Issues and Solutions

### 1. "No response" from Frontend

**Check Backend Logs for:**
```
🤖 [COPILOTKIT] Received /v1/copilotkit request
```

**If you DON'T see this:**
- ✅ Check CORS settings in `backend/main.py`
- ✅ Verify frontend is connecting to `http://localhost:8000`
- ✅ Open browser DevTools → Network tab → Check for failed requests

**If you DO see it:**
- Look for the next logs:
  ```
  🔵 [STREAM] Starting stream
  🔵 [OLLAMA] Calling Ollama
  ```

### 2. Ollama Connection Issues

**Look for:**
```
❌ [ERROR] Exception in stream: ...
```

**Common errors:**
- `Connection refused` → Ollama is not running
  - **Fix:** Run `ollama serve` in a separate terminal
  
- `model 'mistral:latest' not found` → Model not downloaded
  - **Fix:** Run `ollama pull mistral:latest`

- `timeout` → Ollama is slow or overloaded
  - **Fix:** Wait a moment and try again

### 3. Empty or Incomplete Responses

**Check for:**
```
📝 [CHUNK X] Received: ...
```

**If chunks are being received but frontend shows nothing:**
- ✅ Check browser DevTools → Console for errors
- ✅ Verify CopilotKit license key is valid
- ✅ Check SSE connection in Network tab (type: `eventsource`)

### 4. Frontend Not Loading

**Browser Console Errors:**
- `Cannot find module '@copilotkit/react-core'`
  - **Fix:** Run `cd frontend && npm install`

- `publicLicenseKey` errors
  - **Fix:** Verify the license key in `App.tsx`

- CORS errors
  - **Fix:** Check backend CORS settings allow `http://localhost:5173`

## Testing Individual Components

### Test Backend Only
```bash
# Terminal 1: Start backend
./start-backend.sh

# Terminal 2: Test with curl
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

**Expected logs:**
```
🌐 [CHAT] Received /chat request
🔵 [STREAM] Starting stream
🔵 [OLLAMA] Calling Ollama
🟢 [OLLAMA] Stream started successfully
📝 [CHUNK 1] Received: Hello...
✅ [STREAM] Received X chunks
```

### Test Ollama Directly
```bash
curl http://localhost:11434/api/tags
```

Should return list of installed models.

### Test Frontend-Backend Communication

**In Browser DevTools (Network tab):**
1. Look for request to `http://localhost:8000/v1/copilotkit`
2. Check Status: should be `200 OK`
3. Check Type: should be `eventsource` or `text/event-stream`
4. Look at Preview tab: should show SSE events

## Detailed Log Example

Here's what a successful request looks like:

```
============================================================
🤖 [COPILOTKIT] Received /v1/copilotkit request
🤖 [COPILOTKIT] Request keys: ['messages', 'model']
🤖 [COPILOTKIT] Full request: {
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "model": "mistral:latest"
}
============================================================

🤖 [COPILOTKIT] Extracted 1 messages
🤖 [COPILOTKIT] Model: mistral:latest
🤖 [COPILOTKIT] Converted to 1 message objects
  📨 Message 1: [user] Hello

🔵 [STREAM] Starting stream for model: mistral:latest
🔵 [STREAM] Messages count: 1
📤 [EVENT] Sending START event: data: {"type": "start", ...

🔵 [OLLAMA] Calling Ollama with 1 messages
🔵 [OLLAMA] Last message: {'role': 'user', 'content': 'Hello'}
🟢 [OLLAMA] Stream started successfully

📝 [CHUNK 1] Received: Hello...
📝 [CHUNK 2] Received: !...
📝 [CHUNK 3] Received:  How...

✅ [STREAM] Received 25 chunks, total length: 123
📤 [EVENT] Sending RESULT event with 123 chars
📤 [EVENT] Sending END event
```

## Getting Help

If you're still stuck:

1. **Capture the logs:**
   ```bash
   ./start-backend.sh 2>&1 | tee backend.log
   ```

2. **Check the logs for:**
   - Any ❌ error markers
   - The last successful step before failure
   - Full error messages and stack traces

3. **Verify the basics:**
   - [ ] Ollama is running (`ollama serve`)
   - [ ] Model is installed (`ollama list | grep mistral`)
   - [ ] Backend is running (visit http://localhost:8000)
   - [ ] Frontend is running (visit http://localhost:5173)
   - [ ] No port conflicts

4. **Common Port Issues:**
   ```bash
   # Check if ports are in use
   lsof -i :8000  # Backend
   lsof -i :5173  # Frontend
   lsof -i :11434 # Ollama
   ```

## Environment Check

Run this to verify your environment:
```bash
echo "=== Environment Check ==="
echo "Python: $(python --version 2>&1)"
echo "Node: $(node --version 2>&1)"
echo "npm: $(npm --version 2>&1)"
echo ""
echo "=== Ollama Status ==="
curl -s http://localhost:11434/api/tags | head -20
echo ""
echo "=== Backend Status ==="
curl -s http://localhost:8000/ | head -5
```

## Still Need Help?

Review the README files:
- Root: `README.md` - General overview
- Backend: `backend/README.md` - Backend specific
- Frontend: `frontend/README.md` - Frontend specific
