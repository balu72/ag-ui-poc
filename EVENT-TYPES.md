# 📨 AG-UI Protocol Event Types

**Complete Guide to Events Backend Sends to Frontend**

---

## 🎯 Overview

In our AG-UI POC, the backend can send **6 different event types** to the frontend over the SSE stream.

---

## 📋 All Event Types

### **Event Structure**

Every event follows this format:

```typescript
{
  "type": "event_type",      // Type of event
  "data": { ... },           // Event-specific data
  "timestamp": "2025-11-17T..." // When event was created
}
```

**Sent as SSE:**
```
data: {"type":"event_type","data":{...},"timestamp":"..."}

```

---

## 🔹 Event Type 1: `start`

**Purpose:** Signals the beginning of the stream

**When sent:** First event after connection opens

**Data:**
```json
{
  "type": "start",
  "data": {
    "agent": "ollama",
    "model": "mistral:latest"
  },
  "timestamp": "2025-11-17T10:00:00Z"
}
```

**Backend code:**
```python
start_event = create_agui_event(EventType.START, {
    "agent": "ollama",
    "model": model
})
yield start_event
```

**Frontend handling:**
```typescript
if (eventData.type === "start") {
  console.log("Stream started:", eventData.data.agent);
  // Usually just logged, no action needed
}
```

**Example:**
```
User: "Change color to blue"
Backend sends: {"type":"start","data":{"agent":"ollama","model":"mistral:latest"}}
```

---

## 🔹 Event Type 2: `text_message`

**Purpose:** Streams AI response text chunk by chunk

**When sent:** Multiple times during AI response generation

**Data:**
```json
{
  "type": "text_message",
  "data": {
    "content": "Hello",      // Text chunk
    "delta": true,           // Is this a partial chunk?
    "role": "assistant"      // Who's speaking
  },
  "timestamp": "2025-11-17T10:00:01Z"
}
```

**Backend code:**
```python
for chunk in ollama.chat(model, messages, stream=True):
    content = chunk['message']['content']
    event = create_agui_event(EventType.TEXT_MESSAGE, {
        "content": content,
        "delta": True,
        "role": "assistant"
    })
    yield event
```

**Frontend handling:**
```typescript
if (eventData.type === "text_message" && eventData.data.content) {
  // Accumulate text
  assistantMessage += eventData.data.content;
  
  // Update UI with growing message
  setMessages(prev => {
    const newMessages = [...prev];
    newMessages[newMessages.length - 1].content = assistantMessage;
    return newMessages;
  });
}
```

**Example sequence:**
```
Event 1: {"type":"text_message","data":{"content":"Done"}}
Event 2: {"type":"text_message","data":{"content":"!"}}
Event 3: {"type":"text_message","data":{"content":" I've"}}
Event 4: {"type":"text_message","data":{"content":" changed"}}

User sees: "Done" → "Done!" → "Done! I've" → "Done! I've changed"
```

---

## 🔹 Event Type 3: `ui_control`

**Purpose:** Commands frontend to change UI (colors, buttons, etc.)

**When sent:** When backend detects UI command in user message

**Data (Color Change):**
```json
{
  "type": "ui_control",
  "data": {
    "action": "change_theme",
    "color": "#90EE90"
  },
  "timestamp": "2025-11-17T10:00:00Z"
}
```

**Data (Button Addition):**
```json
{
  "type": "ui_control",
  "data": {
    "action": "add_button",
    "label": "Submit"
  },
  "timestamp": "2025-11-17T10:00:00Z"
}
```

**Backend code:**
```python
# Detect color command
if "color" in user_message and "light green" in user_message:
    ui_control_event = json.dumps({
        "type": "ui_control",
        "data": {
            "action": "change_theme",
            "color": "#90EE90"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }) + "\n\n"
    yield f"data: {ui_control_event}"

# Detect button command
if "add" in user_message and "button" in user_message:
    ui_control_event = json.dumps({
        "type": "ui_control",
        "data": {
            "action": "add_button",
            "label": button_label
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }) + "\n\n"
    yield f"data: {ui_control_event}"
```

**Frontend handling:**
```typescript
if (eventData.type === "ui_control") {
  if (eventData.data.action === "change_theme") {
    setThemeColor(eventData.data.color);
    console.log("🎨 Color changed to:", eventData.data.color);
  }
  else if (eventData.data.action === "add_button") {
    setCustomButtons(prev => [...prev, eventData.data.label]);
    console.log("🔘 Button added:", eventData.data.label);
  }
}
```

**Example:**
```
User: "Make it light green"
Backend sends: {"type":"ui_control","data":{"action":"change_theme","color":"#90EE90"}}
Frontend: UI instantly turns light green
```

---

## 🔹 Event Type 4: `result`

**Purpose:** Sends the complete AI response (after all chunks)

**When sent:** After all `text_message` events are sent

**Data:**
```json
{
  "type": "result",
  "data": {
    "content": "Done! I've changed the color to light green.",
    "role": "assistant",
    "model": "mistral:latest"
  },
  "timestamp": "2025-11-17T10:00:05Z"
}
```

**Backend code:**
```python
# After streaming all chunks
full_response = ""  # Accumulated from all chunks

result_event = create_agui_event(EventType.RESULT, {
    "content": full_response,
    "role": "assistant",
    "model": model
})
yield result_event
```

**Frontend handling:**
```typescript
if (eventData.type === "result") {
  console.log("✅ Complete response:", eventData.data.content);
  // Usually just logged - message already shown from text_message events
}
```

**Example:**
```
After all text_message events...
Backend sends: {"type":"result","data":{"content":"Done! I've changed..."}}
```

---

## 🔹 Event Type 5: `end`

**Purpose:** Signals the stream is complete

**When sent:** Last event before connection closes

**Data:**
```json
{
  "type": "end",
  "data": {
    "status": "completed",
    "message_count": 156
  },
  "timestamp": "2025-11-17T10:00:06Z"
}
```

**Backend code:**
```python
# At end of stream
end_event = create_agui_event(EventType.END, {
    "status": "completed",
    "message_count": len(full_response)
})
yield end_event
# Function ends, stream closes
```

**Frontend handling:**
```typescript
if (eventData.type === "end") {
  console.log("🏁 Stream ended");
  // Usually just logged
  // Frontend loop will break after this (done: true)
}
```

**Example:**
```
Backend sends: {"type":"end","data":{"status":"completed"}}
Connection closes shortly after
```

---

## 🔹 Event Type 6: `error`

**Purpose:** Reports errors during processing

**When sent:** When something goes wrong

**Data:**
```json
{
  "type": "error",
  "data": {
    "error": "Connection to Ollama failed",
    "message": "Failed to generate response from Ollama"
  },
  "timestamp": "2025-11-17T10:00:02Z"
}
```

**Backend code:**
```python
try:
    # ... process request ...
except Exception as e:
    error_event = create_agui_event(EventType.ERROR, {
        "error": str(e),
        "message": "Failed to generate response from Ollama"
    })
    yield error_event
```

**Frontend handling:**
```typescript
if (eventData.type === "error") {
  console.error("❌ Error:", eventData.data.message);
  // Show error message to user
  setMessages(prev => [...prev, {
    role: "assistant",
    content: "Sorry, there was an error: " + eventData.data.message
  }]);
}
```

**Example:**
```
If Ollama crashes...
Backend sends: {"type":"error","data":{"error":"Connection failed"}}
Frontend shows: "Sorry, there was an error: Connection failed"
```

---

## 📊 Event Flow Example

**User types:** "Change color to light green"

### **Complete Event Sequence:**

```
T=50ms: UI Control
data: {"type":"ui_control","data":{"action":"change_theme","color":"#90EE90"}}
→ UI turns light green

T=100ms: Start
data: {"type":"start","data":{"agent":"ollama","model":"mistral:latest"}}
→ Logged

T=200ms: Text chunk 1
data: {"type":"text_message","data":{"content":"Done"}}
→ Shows "Done"

T=220ms: Text chunk 2
data: {"type":"text_message","data":{"content":"!"}}
→ Shows "Done!"

T=240ms: Text chunk 3
data: {"type":"text_message","data":{"content":" I've"}}
→ Shows "Done! I've"

T=260ms: Text chunk 4
data: {"type":"text_message","data":{"content":" changed"}}
→ Shows "Done! I've changed"

... more chunks ...

T=2000ms: Result
data: {"type":"result","data":{"content":"Done! I've changed the color..."}}
→ Logged

T=2001ms: End
data: {"type":"end","data":{"status":"completed"}}
→ Stream ends
```

---

## 🔧 Backend: Event Type Definitions

```python
class EventType:
    TEXT_MESSAGE = "text_message"  # AI response chunks
    AGENT_STATE = "agent_state"    # Agent status (not used in POC)
    RESULT = "result"              # Complete response
    ERROR = "error"                # Error occurred
    START = "start"                # Stream started
    END = "end"                    # Stream ended
    # UI_CONTROL is custom, not in base class
```

---

## 🎨 Custom Event: `ui_control`

**Special event type we added for AG-UI protocol!**

### **Supported Actions:**

#### **1. Change Theme Color**
```json
{
  "type": "ui_control",
  "data": {
    "action": "change_theme",
    "color": "#FF0000"  // Any hex color
  }
}
```

#### **2. Add Button**
```json
{
  "type": "ui_control",
  "data": {
    "action": "add_button",
    "label": "Click Me"  // Button text
  }
}
```

### **Easy to Extend!**

Want to add more UI controls? Just add new actions:

```json
{
  "type": "ui_control",
  "data": {
    "action": "show_modal",
    "title": "Alert",
    "message": "Important!"
  }
}
```

```typescript
// Frontend handling
else if (eventData.data.action === "show_modal") {
  showModal(eventData.data.title, eventData.data.message);
}
```

---

## 📋 Quick Reference Table

| Event Type | When | Purpose | Frontend Action |
|------------|------|---------|----------------|
| `start` | First | Stream beginning | Log |
| `text_message` | Multiple | AI response chunks | Append to message |
| `ui_control` | When detected | Change UI | Update color/buttons |
| `result` | After text | Complete response | Log |
| `end` | Last | Stream complete | Break loop |
| `error` | On error | Report problem | Show error |

---

## 🎯 Summary

**Backend can send 6 event types:**

1. ✅ **start** - Stream begins
2. ✅ **text_message** - AI text (many times)
3. ✅ **ui_control** - Change UI (custom!)
4. ✅ **result** - Complete response
5. ✅ **end** - Stream ends
6. ✅ **error** - Something wrong

**Each event has:**
- `type` - What kind of event
- `data` - Event-specific information
- `timestamp` - When it was created

**Frontend must handle each type appropriately!**

---

## 🚀 Adding New Event Types

**Want to add a new event type?**

### **Backend:**
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

### **Frontend:**
```typescript
// 3. Handle in frontend
else if (eventData.type === "my_new_event") {
  handleMyNewEvent(eventData.data);
}
```

**That's it! The AG-UI protocol is extensible!** 🎨
