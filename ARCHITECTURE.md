# 🏗️ AG-UI POC Architecture Guide

This document explains every file in the project and how they work together.

---

## 📁 Project Structure

```
AG-UI-POC/
├── backend/              # Python FastAPI server
│   ├── main.py          # Main backend logic
│   ├── requirements.txt # Python dependencies
│   └── README.md        # Backend documentation
├── frontend/            # React TypeScript client
│   ├── src/
│   │   ├── App.tsx      # Main React component
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

---

## 🔧 Backend Files

### **1. backend/main.py** (Main Backend Logic)

**Purpose:** FastAPI server implementing AG-UI protocol

**Key Components:**

#### **Imports & Setup**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ollama
```
- FastAPI for REST API
- CORS for frontend communication
- Ollama for LLM integration

#### **Data Models**
```python
class Message(BaseModel):
    role: str      # "user", "assistant", or "system"
    content: str   # Message text

class ChatRequest(BaseModel):
    messages: List[Message]  # Conversation history
    model: Optional[str]     # Ollama model name
```

#### **AG-UI Event Types**
```python
class EventType:
    TEXT_MESSAGE = "text_message"  # Streaming text chunks
    START = "start"                # Stream started
    END = "end"                    # Stream ended
    ERROR = "error"                # Error occurred
    RESULT = "result"              # Complete response
```

#### **Core Function: stream_ollama_response()**

**What it does:**
1. **Detects UI Commands** in user message
   - Color changes: "change color to light green"
   - Button additions: "add a button 'Test'"

2. **Sends UI Control Events** (if detected)
   ```python
   {
     "type": "ui_control",
     "data": {
       "action": "change_theme",
       "color": "#FFB347"
     }
   }
   ```

3. **Calls Ollama** to generate AI response

4. **Streams Response** as AG-UI events
   - START → TEXT_MESSAGE (many) → RESULT → END

5. **Handles Errors** gracefully

#### **API Endpoints**

**`GET /`** - Health check
```json
{
  "service": "AG-UI POC Backend",
  "status": "running",
  "protocol": "AG-UI"
}
```

**`GET /health`** - Ollama connection check
```json
{
  "status": "healthy",
  "ollama": "connected",
  "available_models": ["mistral:latest", ...]
}
```

**`POST /chat`** - Main chat endpoint
- Accepts: ChatRequest (messages + model)
- Returns: SSE stream of AG-UI events
- Headers: 
  - `Content-Type: text/event-stream`
  - `Cache-Control: no-cache`

---

### **2. backend/requirements.txt**

**Purpose:** Python dependencies

```
fastapi        # Web framework
uvicorn        # ASGI server
ollama         # Ollama client
pydantic       # Data validation
```

**Install:** `pip install -r requirements.txt`

---

### **3. backend/README.md**

**Purpose:** Backend-specific documentation

**Contains:**
- Setup instructions
- How to run the server
- API endpoint details
- Ollama configuration

---

## 🎨 Frontend Files

### **1. frontend/src/App.tsx** (Main React Component)

**Purpose:** Chat UI that communicates with backend

**State Management:**
```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [themeColor, setThemeColor] = useState("#646cff");
const [customButtons, setCustomButtons] = useState<string[]>([]);
const [isLoading, setIsLoading] = useState(false);
```

**Key Functions:**

#### **sendMessage()** - Main chat logic
1. Adds user message to state
2. Sends POST to `http://localhost:8000/chat`
3. Reads SSE stream using ReadableStream API
4. Parses AG-UI events:
   ```typescript
   if (eventData.type === "text_message") {
     // Append to assistant message
   } else if (eventData.type === "ui_control") {
     // Update UI (color or buttons)
   }
   ```

#### **Event Handling:**
```typescript
// Color change
if (eventData.data.action === "change_theme") {
  setThemeColor(eventData.data.color);
}

// Button addition
else if (eventData.data.action === "add_button") {
  setCustomButtons(prev => [...prev, eventData.data.label]);
}
```

#### **UI Structure:**
```tsx
<div className="app-container">
  <header>
    {/* Title, badges */}
  </header>
  
  <main className="chat-container">
    <div className="messages">
      {/* Message bubbles */}
    </div>
    <div className="input-container">
      {/* Textarea + Send button */}
    </div>
  </main>
  
  <footer>
    {/* Dynamic buttons */}
  </footer>
</div>
```

---

### **2. frontend/src/App.css**

**Purpose:** Styles for the chat interface

**Key Sections:**

- `.app-container` - Main layout (flexbox column)
- `.app-header` - Title and badges
- `.chat-container` - Chat area with overflow
- `.messages` - Scrollable message list
- `.message.user` - User message (right-aligned, blue)
- `.message.assistant` - AI message (left-aligned, gray)
- `.input-container` - Input field + send button
- `.custom-buttons` - Dynamic buttons area

**Dynamic Theming:**
```css
background: themeColor;  /* Applied via inline styles */
```

---

### **3. frontend/src/main.tsx**

**Purpose:** React application entry point

```typescript
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- Mounts React app to `#root` div
- Wraps in StrictMode for development checks

---

### **4. frontend/src/index.css**

**Purpose:** Global CSS styles

- Reset styles
- Dark mode colors
- Font imports
- Base element styles

---

### **5. frontend/index.html**

**Purpose:** HTML entry point

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>AG-UI POC</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

---

### **6. frontend/package.json**

**Purpose:** Node.js project configuration

**Dependencies:**
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1"
}
```

**Scripts:**
```json
{
  "dev": "vite",           # Start dev server
  "build": "tsc && vite build",  # Build for production
  "preview": "vite preview"      # Preview production build
}
```

---

### **7. frontend/vite.config.ts**

**Purpose:** Vite bundler configuration

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    cors: true
  }
})
```

---

### **8. frontend/tsconfig.json**

**Purpose:** TypeScript compiler configuration

- Enables JSX support
- Sets module resolution
- Configures type checking

---

## 🔄 How Data Flows

### **1. User Sends Message**
```
User types "Change color to light green"
  ↓
App.tsx: sendMessage() called
  ↓
POST http://localhost:8000/chat
```

### **2. Backend Processes**
```
FastAPI receives request
  ↓
stream_ollama_response() function
  ↓
Detects "color" + "light green"
  ↓
Sends ui_control event first
  ↓
Calls Ollama for AI response
  ↓
Streams text_message events
```

### **3. Frontend Updates**
```
SSE stream reader receives events
  ↓
Parses JSON events
  ↓
ui_control event: setThemeColor("#90EE90")
  ↓
text_message events: Append to assistant message
  ↓
UI re-renders with new color
```

---

## 🛠️ Helper Scripts

### **start-backend.sh**
```bash
#!/bin/bash
cd backend
source venv/bin/activate  # Activate virtual env
python main.py            # Start server
```

### **start-frontend.sh**
```bash
#!/bin/bash
cd frontend
npm run dev              # Start Vite dev server
```

### **test-backend.sh**
```bash
#!/bin/bash
# Tests:
# 1. Backend accessibility
# 2. Ollama connection
# 3. Send test message
```

---

## 📚 Documentation Files

### **README.md**
- Project overview
- Quick start guide
- Features list
- Architecture diagram

### **DEBUGGING.md**
- Emoji log meanings (🎨 🔘 ✅ ❌)
- Common issues & solutions
- Testing instructions
- Environment checks

### **backend/README.md**
- Backend-specific docs
- API endpoint details
- Ollama setup

### **frontend/README.md**
- Frontend-specific docs
- Component structure
- State management

---

## 🔑 Key Concepts

### **AG-UI Protocol**
A protocol for agent-user interaction using:
- **REST** for requests
- **SSE** (Server-Sent Events) for streaming
- **Structured events** (type + data + timestamp)

### **SSE (Server-Sent Events)**
```
data: {"type": "text_message", "data": {...}}

data: {"type": "ui_control", "data": {...}}

```
- One-way server → client
- Text-based format
- Automatic reconnection

### **UI Control Events**
Custom AG-UI event type enabling:
- Agent controls frontend UI
- Theme changes
- Dynamic component generation
- Real-time updates

---

## 🎯 Adding New UI Controls

**1. Add backend detection:**
```python
if "action" in last_message:
    yield create_ui_control_event({
        "action": "new_action",
        "data": {...}
    })
```

**2. Add frontend handler:**
```typescript
else if (eventData.data.action === "new_action") {
  // Handle the action
}
```

**3. Update UI:**
```typescript
// Add state if needed
const [newState, setNewState] = useState(...);
```

---

## 🚀 Summary

**Backend (backend/main.py):**
- FastAPI server
- Ollama integration
- AG-UI event generation
- UI command detection

**Frontend (frontend/src/App.tsx):**
- React chat interface
- SSE stream handling
- Dynamic UI updates
- State management

**Communication:**
- REST: Frontend → Backend
- SSE: Backend → Frontend
- Protocol: AG-UI events

**Magic:**
- AI detects commands in natural language
- Backend sends UI control events
- Frontend updates in real-time
- Agent-driven interface! 🎨🤖
