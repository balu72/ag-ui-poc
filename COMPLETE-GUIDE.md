# 📖 AG-UI Protocol POC - Complete Guide

**The Comprehensive Documentation for Understanding Agent-Driven User Interfaces**

---

## 📑 Table of Contents

1. [Introduction](#-1-introduction)
2. [Project Architecture](#-2-project-architecture)
3. [AG-UI Protocol Deep Dive](#-3-ag-ui-protocol-deep-dive)
4. [SSE (Server-Sent Events) Explained](#-4-sse-server-sent-events-explained)
5. [Event Types Reference](#-5-event-types-reference)
6. [Frontend Implementation](#-6-frontend-implementation)
7. [Adding New Features](#-7-adding-new-features)
8. [Quick Reference](#-8-quick-reference)

---

## 📌 1. Introduction

### What is AG-UI Protocol?

**AG-UI = Agent-User Interface Protocol**

A standardized protocol for enabling AI agents to control user interfaces in real-time through natural language commands.

### Key Features of This POC

✅ **Natural Language UI Control** - Change colors, add buttons via chat  
✅ **Real-time Streaming** - AI responses appear word-by-word  
✅ **Pure REST + SSE** - No WebSocket, no GraphQL complexity  
✅ **Dynamic UI** - Agent controls interface elements  
✅ **Extensible** - Easy to add new UI controls

### Technology Stack

**Frontend:**
- React + TypeScript
- Vite (Build tool)
- Fetch API (HTTP requests)
- ReadableStream API (SSE handling)

**Backend:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Ollama (Local LLM runtime)
- Pydantic (Data validation)

**AI:**
- Ollama with mistral:latest model

---

## 🏗️ 2. Project Architecture

### 📁 Project Structure

```
AG-UI-POC/
├── backend/              # Python FastAPI server
│   ├── main.py          # Main backend logic (350+ lines)
│   ├── requirements.txt # Python dependencies
│   └── README.md        # Backend documentation
├── frontend/            # React TypeScript client
│   ├── src/
│   │   ├── App.tsx      # Main React component (200+ lines)
│   │   ├── App.css      # Component styles
│   │   ├── main.tsx     # React entry point
│   │   └── index.css    # Global styles
│   ├── package.json     # Node dependencies
│   ├── vite.config.ts   # Vite bundler config
│   ├── tsconfig.json    # TypeScript config
│   └── index.html       # HTML entry point
├── start-backend.sh     # Helper: Start backend
├── start-frontend.sh    # Helper: Start frontend
├── test-backend.sh      # Helper: Test backend
├── DEBUGGING.md         # Troubleshooting guide
├── README.md            # Main documentation
└── .gitignore          # Git ignore rules
```

### 🔄 Data Flow

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │  REST   │              │  Calls  │              │
│   Frontend   │────────▶│   Backend    │────────▶│   Ollama     │
│   (React)    │         │  (FastAPI)   │         │   (LLM)      │
│              │◀────────│              │◀────────│              │
└──────────────┘   SSE   └──────────────┘ Streams └──────────────┘
       ▲                        │
       │                        │
       │    UI Control          │ Detects
       │      Events            │ Commands
       │                        │
       └────────────────────────┘
```

**Flow:**
1. User types natural language command
2. Frontend sends POST to `/chat` endpoint
3. Backend detects UI commands in message
4. Backend calls Ollama for AI response
5. Backend streams both UI events + AI text
6. Frontend updates UI in real-time

---

## 🔧 3. AG-UI Protocol Deep Dive

### What Makes AG-UI Different?

Traditional UIs are **static** - users click buttons to make things happen.

AG-UI enables **dynamic** UIs - agents control the interface through natural language.

### Protocol Components

#### 1. REST API (Request)
```http
POST /chat HTTP/1.1
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Change color to light green"}
  ],
  "model": "mistral:latest"
}
```

#### 2. SSE Stream (Response)
```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Connection: keep-alive

data: {"type":"ui_control","data":{"action":"change_theme","color":"#90EE90"}}

data: {"type":"start","data":{"agent":"ollama"}}

data: {"type":"text_message","data":{"content":"Done!"}}

data: {"type":"end","data":{"status":"completed"}}

```

#### 3. Structured Events
```typescript
{
  "type": "event_type",      // What kind of event
  "data": { ... },           // Event-specific data
  "timestamp": "2025-..."    // When it was created
}
```

### Backend Implementation

**Main components in `backend/main.py`:**

#### Data Models
```python
class Message(BaseModel):
    role: str      # "user", "assistant", "system"
    content: str   # Message text

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "mistral:latest"

class AGUIEvent(BaseModel):
    type: str
    data: dict
    timestamp: Optional[str] = None
```

#### Event Types
```python
class EventType:
    TEXT_MESSAGE = "text_message"  # AI response chunks
    START = "start"                # Stream started
    END = "end"                    # Stream ended
    ERROR = "error"                # Error occurred
    RESULT = "result"              # Complete response
```

#### Core Function
```python
async def stream_ollama_response(messages: List[Message], model: str):
    # 1. Detect UI commands
    if "color" in user_message and "light green" in user_message:
        yield ui_control_event({"action": "change_theme", "color": "#90EE90"})
    
    # 2. Send start event
    yield create_agui_event(EventType.START, {"agent": "ollama"})
    
    # 3. Stream AI response
    for chunk in ollama.chat(model, messages, stream=True):
        yield create_agui_event(EventType.TEXT_MESSAGE, {
            "content": chunk['message']['content']
        })
    
    # 4. Send end event
    yield create_agui_event(EventType.END, {"status": "completed"})
```

#### API Endpoints

**GET /** - Health check
```python
@app.get("/")
async def root():
    return {
        "service": "AG-UI POC Backend",
        "status": "running"
    }
```

**GET /health** - Ollama connection check
```python
@app.get("/health")
async def health_check():
    models = ollama.list()
    return {
        "status": "healthy",
        "available_models": [m['name'] for m in models['models']]
    }
```

**POST /chat** - Streaming chat endpoint
```python
@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        stream_ollama_response(request.messages, request.model),
        media_type="text/event-stream"
    )
```

---

## 📡 4. SSE (Server-Sent Events) Explained

### SSE vs Traditional REST

#### Traditional REST:
```
Client → Request → Server
Client ← Response ← Server
[Connection closes] ✅
```

#### SSE (Our POC):
```
Client → Request → Server
Client ← Event 1 ← Server
Client ← Event 2 ← Server  [Connection stays open]
Client ← Event 3 ← Server
[Connection closes when stream ends] ✅
```

### How SSE Works with REST

**Key Insight:** SSE doesn't bypass REST - it extends it!

#### Step 1: Normal REST Request
```typescript
const response = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({messages, model})
});
```

This is a standard HTTP POST request!

#### Step 2: Special Response Headers
```python
return StreamingResponse(
    stream_ollama_response(...),
    media_type="text/event-stream",  # ← Tells client this is SSE
    headers={
        "Connection": "keep-alive",   # ← Keep connection open
        "Cache-Control": "no-cache"
    }
)
```

#### Step 3: Connection Stays Open
```
Normal REST:
───────────────────────────────────
Client                     Server
  │                           │
  ├──── POST /chat ──────────▶│
  │◀──── {response} ──────────┤
  X (closed)                  X

SSE Stream:
───────────────────────────────────
Client                     Server
  │                           │
  ├──── POST /chat ──────────▶│
  │◀─── data: event1 ─────────┤
  │◀─── data: event2 ─────────┤  Connection
  │◀─── data: event3 ─────────┤  stays open!
  X (closed after stream)     X
```

### Why SSE for This POC?

✅ **Simpler than WebSocket** - Just HTTP  
✅ **Automatic reconnection** - Browser handles it  
✅ **Text-based** - Easy to debug  
✅ **One direction** - Server → Client (what we need)  
✅ **Built into HTTP** - No extra protocols

### Frontend Handling: Two Patterns

#### Pattern 1: Regular REST Endpoint
```typescript
// For GET /, GET /health
const response = await fetch("/health");
const data = await response.json();  // ← Simple!
console.log(data.status);
```

#### Pattern 2: Streaming REST Endpoint
```typescript
// For POST /chat
const response = await fetch("/chat", {...});
const reader = response.body.getReader();  // ← Get reader

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  parseAndHandle(chunk);  // Process each chunk
}
```

**Key Difference:**

| Aspect | Regular REST | Streaming REST |
|--------|--------------|----------------|
| **Parse method** | `response.json()` | `response.body.getReader()` |
| **Waiting** | Single `await` | Loop with multiple `await` |
| **Data arrival** | All at once | Piece by piece |
| **Processing** | Once | Multiple times |
| **UI updates** | Once at end | Multiple times during |

---

## 📨 5. Event Types Reference

### All Event Types

The backend can send **6 different event types** to the frontend:

---

### 🔹 1. `start`

**Purpose:** Signals stream beginning

**When sent:** First event after connection opens

**Data:**
```json
{
  "type": "start",
  "data": {
    "agent": "ollama",
    "model": "mistral:latest"
  }
}
```

**Frontend handling:**
```typescript
if (eventData.type === "start") {
  console.log("Stream started");
}
```

---

### 🔹 2. `text_message`

**Purpose:** Streams AI response text chunk by chunk

**When sent:** Multiple times during AI generation

**Data:**
```json
{
  "type": "text_message",
  "data": {
    "content": "Hello",
    "delta": true,
    "role": "assistant"
  }
}
```

**Frontend handling:**
```typescript
if (eventData.type === "text_message") {
  assistantMessage += eventData.data.content;
  updateUI(assistantMessage);  // Update UI for each chunk
}
```

**Example sequence:**
```
Event 1: {"content":"Done"}
Event 2: {"content":"!"}
Event 3: {"content":" I've"}

User sees: "Done" → "Done!" → "Done! I've"
```

---

### 🔹 3. `ui_control` ⭐

**Purpose:** Commands frontend to change UI

**When sent:** When backend detects UI command

**Data (Color Change):**
```json
{
  "type": "ui_control",
  "data": {
    "action": "change_theme",
    "color": "#90EE90"
  }
}
```

**Data (Button Addition):**
```json
{
  "type": "ui_control",
  "data": {
    "action": "add_button",
    "label": "Submit"
  }
}
```

**Backend detection:**
```python
# Color change
if "color" in user_message and "light green" in user_message:
    yield ui_control_event({
        "action": "change_theme",
        "color": "#90EE90"
    })

# Button addition
if "add" in user_message and "button" in user_message:
    yield ui_control_event({
        "action": "add_button",
        "label": "Submit"
    })
```

**Frontend handling:**
```typescript
if (eventData.type === "ui_control") {
  if (eventData.data.action === "change_theme") {
    setThemeColor(eventData.data.color);
  }
  else if (eventData.data.action === "add_button") {
    setCustomButtons(prev => [...prev, eventData.data.label]);
  }
}
```

---

### 🔹 4. `result`

**Purpose:** Complete AI response (after all chunks)

**When sent:** After all `text_message` events

**Data:**
```json
{
  "type": "result",
  "data": {
    "content": "Done! I've changed the color.",
    "role": "assistant"
  }
}
```

**Frontend handling:**
```typescript
if (eventData.type === "result") {
  console.log("✅ Complete response received");
}
```

---

### 🔹 5. `end`

**Purpose:** Signals stream complete

**When sent:** Last event before connection closes

**Data:**
```json
{
  "type": "end",
  "data": {
    "status": "completed"
  }
}
```

**Frontend handling:**
```typescript
if (eventData.type === "end") {
  console.log("🏁 Stream ended");
  // Loop will break after this (done: true)
}
```

---

### 🔹 6. `error`

**Purpose:** Reports errors

**When sent:** When something goes wrong

**Data:**
```json
{
  "type": "error",
  "data": {
    "error": "Connection failed",
    "message": "Failed to generate response"
  }
}
```

**Frontend handling:**
```typescript
if (eventData.type === "error") {
  console.error("❌ Error:", eventData.data.message);
  showErrorToUser(eventData.data.message);
}
```

---

### Event Flow Example

**User types:** "Change color to light green"

```
T=50ms:   ui_control    → UI turns light green
T=100ms:  start         → Logged
T=200ms:  text_message  → "Done"
T=220ms:  text_message  → "!"
T=240ms:  text_message  → " I've"
T=260ms:  text_message  → " changed"
...
T=2000ms: result        → Complete response
T=2001ms: end           → Stream closes
```

---

## 🎨 6. Frontend Implementation

### State Management

```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [themeColor, setThemeColor] = useState("#646cff");
const [customButtons, setCustomButtons] = useState<string[]>([]);
const [isLoading, setIsLoading] = useState(false);
```

### The sendMessage() Function

**Step-by-step breakdown:**

#### Step 1: Add User Message
```typescript
const userMessage = { role: "user", content: input };
setMessages(prev => [...prev, userMessage]);
setInput("");
setIsLoading(true);
```

#### Step 2: Send POST Request
```typescript
const response = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    messages: [...messages, userMessage],
    model: "mistral:latest"
  })
});
```

#### Step 3: Get Stream Reader
```typescript
const reader = response.body?.getReader();
const decoder = new TextDecoder();
let assistantMessage = "";
```

#### Step 4: Prepare UI
```typescript
// Add empty assistant message that we'll update
setMessages(prev => [
  ...prev,
  { role: "assistant", content: "" }
]);
```

#### Step 5: Read Stream Loop
```typescript
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split("\n");
  
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const eventData = JSON.parse(line.substring(6));
      handleEvent(eventData);
    }
  }
}
```

#### Step 6: Handle Events
```typescript
function handleEvent(eventData) {
  if (eventData.type === "text_message") {
    assistantMessage += eventData.data.content;
    setMessages(prev => {
      const newMessages = [...prev];
      newMessages[newMessages.length - 1].content = assistantMessage;
      return newMessages;
    });
  }
  else if (eventData.type === "ui_control") {
    if (eventData.data.action === "change_theme") {
      setThemeColor(eventData.data.color);
    }
    else if (eventData.data.action === "add_button") {
      setCustomButtons(prev => [...prev, eventData.data.label]);
    }
  }
}
```

### UI Structure

```tsx
<div className="app-container" style={{ '--theme-color': themeColor }}>
  <header style={{ borderBottomColor: themeColor }}>
    <h1>🤖 AG-UI POC</h1>
  </header>
  
  <main className="chat-container">
    <div className="messages">
      {messages.map((message, index) => (
        <div className={`message ${message.role}`}>
          {message.content}
        </div>
      ))}
    </div>
    
    <div className="input-container">
      <textarea value={input} onChange={...} />
      <button onClick={sendMessage}>Send</button>
    </div>
  </main>
  
  <footer>
    {customButtons.map((label) => (
      <button style={{ background: themeColor }}>
        {label}
      </button>
    ))}
  </footer>
</div>
```

### How UI Updates Work

**State Update → React Re-render → DOM Update**

```typescript
// 1. State changes
setThemeColor("#90EE90");

// 2. React re-renders components using themeColor
<header style={{ borderBottomColor: themeColor }}>
<button style={{ background: themeColor }}>

// 3. User sees new color instantly
```

**Every setState call causes React to re-render affected components!**

---

## 🚀 7. Adding New Features

### Adding a New UI Control

**Example: Add "show_notification" action**

#### Backend
```python
# Detect notification command
if "notify" in user_message:
    title = extract_title(user_message)
    message = extract_message(user_message)
    
    yield ui_control_event({
        "action": "show_notification",
        "title": title,
        "message": message
    })
```

#### Frontend
```typescript
// Add state
const [notification, setNotification] = useState(null);

// Handle event
else if (eventData.data.action === "show_notification") {
  setNotification({
    title: eventData.data.title,
    message: eventData.data.message
  });
}

// Render
{notification && (
  <div className="notification">
    <h3>{notification.title}</h3>
    <p>{notification.message}</p>
  </div>
)}
```

### Adding a New Event Type

#### Backend
```python
# 1. Define in EventType class
class EventType:
    MY_NEW_EVENT = "my_new_event"

# 2. Create and send event
new_event = create_agui_event(EventType.MY_NEW_EVENT, {
    "custom_data": "value"
})
yield new_event
```

#### Frontend
```typescript
// 3. Handle in frontend
else if (eventData.type === "my_new_event") {
  handleMyNewEvent(eventData.data);
}
```

---

## 📋 8. Quick Reference

### Backend Endpoints

| Endpoint | Method | Purpose | Response Type |
|----------|--------|---------|---------------|
| `/` | GET | Health check | Single JSON |
| `/health` | GET | Ollama status | Single JSON |
| `/chat` | POST | Chat with streaming | SSE Stream |

### Event Types

| Type | Purpose | Frequency |
|------|---------|-----------|
| `start` | Stream beginning | Once (first) |
| `text_message` | AI response chunks | Many |
| `ui_control` | Change UI | When detected |
| `result` | Complete response | Once |
| `end` | Stream complete | Once (last) |
| `error` | Error occurred | On error |

### UI Control Actions

| Action | Purpose | Data |
|--------|---------|------|
| `change_theme` | Change color | `{color: "#HEX"}` |
| `add_button` | Add button | `{label: "Text"}` |

### Commands to Try

```
"Change color to light green"
"Make it purple"
"Add a button 'Submit'"
"Create a 'Test' button"
"Make it dark blue and add a Download button"
```

### File Structure

```
Backend:  backend/main.py          (350+ lines)
Frontend: frontend/src/App.tsx     (200+ lines)
Docs:     COMPLETE-GUIDE.md        (This file!)
```

### Quick Start

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Visit: http://localhost:5174
```

### Key Concepts

**SSE:** Server-Sent Events - HTTP streaming from server to client  
**AG-UI:** Agent-User Interface - AI controls UI  
**REST:** Standard HTTP API  
**Event:** Structured message with type + data  
**Stream:** One connection, multiple messages over time  

---

## 🎯 Summary

**What We Built:**
- ✅ AG-UI protocol implementation
- ✅ Natural language UI control
- ✅ Real-time streaming responses
- ✅ Dynamic theming & components
- ✅ Extensible architecture

**How It Works:**
1. User sends natural language command
2. Backend detects UI commands
3. Backend sends UI control events
4. Backend streams AI response
5. Frontend updates UI in real-time

**Why It Matters:**
- 🗣️ Natural interaction
- ⚡ Instant results
- 🎨 Dynamic interfaces
- 🤖 Agent autonomy
- 🚀 Future of UIs

**The Magic:**
AI agents can control UIs through standardized events, enabling true agent-driven interfaces!

---

## 📚 Additional Resources

- **GitHub:** https://github.com/balu72/ag-ui-poc.git
- **README.md:** Project overview
- **DEBUGGING.md:** Troubleshooting guide
- **PRESENTATION.md:** Presentation slides
- **Backend README:** API documentation
- **Frontend README:** Component docs

---

**Built with Pure AG-UI Protocol (REST + SSE) | Powered by Ollama & Mistral**

🎉 **Welcome to the future of agent-driven interfaces!** 🎉

---

## ❓ FAQ (Frequently Asked Questions)

### **Q: Are we showing the response as a stream in real-time? Is that the only advantage of AG-UI protocol?**

**A: Yes, we stream in real-time, but that's only PART of the AG-UI advantage!**

#### **What We're Actually Doing:**

**1. Real-time Streaming (SSE) ✅**

Yes, the LLM response appears **word-by-word in real-time**!

**You can see this when you type a message:**
```
User: "What is AI?"

Frontend shows (progressively):
T=200ms: "Artificial"
T=220ms: "Artificial Intelligence"
T=240ms: "Artificial Intelligence is"
T=260ms: "Artificial Intelligence is a"
...continues...
```

**Without streaming (traditional):**
```
User: "What is AI?"
[Wait 2 seconds...]
Frontend shows: "Artificial Intelligence is a field of computer science..."
```

**Code that makes this happen:**
```typescript
// Frontend receives each chunk
if (eventData.type === "text_message") {
  assistantMessage += eventData.data.content;  // ← Accumulate
  updateUI(assistantMessage);  // ← Update UI immediately
}
```

---

**2. UI Control (AG-UI Protocol) ⭐ - The REAL Magic**

But **streaming alone is NOT AG-UI protocol!**

The **true power** of AG-UI protocol is the **UI Control Events**:

```
User: "Change color to light green"

What happens:
1. Backend detects "color" command
2. Sends UI_CONTROL event IMMEDIATELY
3. Frontend changes color INSTANTLY (before AI even responds)
4. Then AI response streams
```

**This is the AG-UI advantage:**
```typescript
// AI can control the UI!
if (eventData.type === "ui_control") {
  if (eventData.data.action === "change_theme") {
    setThemeColor(eventData.data.color);  // ← UI changes!
  }
}
```

---

#### **AG-UI Protocol = Streaming + UI Control**

**Two Advantages Combined:**

**Advantage 1: Real-time Streaming (SSE)**
- See AI response word-by-word
- Better UX
- Feels alive
- **Many chatbots do this!**

**Advantage 2: UI Control (AG-UI Special!)** ⭐
- AI controls the interface
- Changes colors
- Adds buttons
- Could add forms, charts, modals, etc.
- **This is unique to AG-UI!**

---

#### **Comparison:**

**Traditional Chatbot:**
```
User: "Change color to blue"
AI: "I'm sorry, I can't change colors. Please click the theme button."
```
**AI can only talk, can't act!**

**Our AG-UI POC:**
```
User: "Change color to blue"
[UI instantly turns blue]
AI: "Done! I've changed the color to blue."
```
**AI can talk AND act!**

---

#### **What Makes AG-UI Special?**

Not just streaming (that's SSE - common)

**But the combination:**
1. ✅ Natural language UI commands
2. ✅ Backend detects intent
3. ✅ **Sends UI control events** ⭐
4. ✅ Frontend executes UI changes
5. ✅ Streams AI response

---

#### **The Key Insight:**

**Streaming alone:** Good UX, but AI is just talking

**AG-UI Protocol:** AI is **doing things** - controlling the interface!

```
Traditional: User → Click buttons → UI changes
AG-UI:      User → Say command → AI changes UI
```

---

#### **Try This in the POC:**

**1. Just chat (streaming only):**
```
"What is AG-UI protocol?"
→ Response streams word-by-word ✅
→ But UI doesn't change
```

**2. UI command (AG-UI protocol!):**
```
"Change color to light green"
→ UI turns green INSTANTLY! ⭐
→ THEN response streams ✅
```

**The instant UI change is the AG-UI magic!**

---

#### **Summary:**

✅ **YES, we stream in real-time** (word-by-word responses)

❌ **NO, that's not the only AG-UI advantage**

⭐ **The MAIN AG-UI advantage is UI Control Events** - where the AI can actually manipulate the interface through standardized events!

**AG-UI = Streaming (good) + UI Control (revolutionary)**

**Streaming makes it feel alive, UI Control makes it intelligent!** 🤖✨
