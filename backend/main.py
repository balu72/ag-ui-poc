"""
AG-UI POC Backend with FastAPI and Ollama
Implements AG-UI protocol for agent-user interaction
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncIterator
import ollama
import json
import asyncio
from datetime import datetime, timezone
import sys

app = FastAPI(title="AG-UI POC Backend")

# Force print statements to flush immediately
sys.stdout.reconfigure(line_buffering=True)

# CORS configuration for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "mistral:latest"

class AGUIEvent(BaseModel):
    """AG-UI Protocol Event Structure"""
    type: str
    data: dict
    timestamp: Optional[str] = None

# AG-UI Protocol Event Types
class EventType:
    TEXT_MESSAGE = "text_message"
    AGENT_STATE = "agent_state"
    RESULT = "result"
    ERROR = "error"
    START = "start"
    END = "end"

def create_agui_event(event_type: str, data: dict) -> str:
    """Create AG-UI protocol compliant event"""
    event = AGUIEvent(
        type=event_type,
        data=data,
        timestamp=datetime.utcnow().isoformat()
    )
    return f"data: {json.dumps(event.dict())}\n\n"

async def stream_ollama_response(messages: List[Message], model: str) -> AsyncIterator[str]:
    """Stream responses from Ollama with AG-UI protocol events"""
    
    print(f"🔵 [STREAM] Starting stream for model: {model}", flush=True)
    print(f"🔵 [STREAM] Messages count: {len(messages)}", flush=True)
    
    # Check if user is requesting a UI change (color change)
    color_changed = False
    detected_color = ""
    if messages:
        last_message = messages[-1].content.lower()
        
        # Simple color detection
        color_keywords = {
            "light orange": "#FFB347",
            "light green": "#90EE90",
            "light blue": "#87CEEB",
            "light red": "#FF6B6B",
            "light purple": "#DDA0DD",
            "light pink": "#FFB6C1",
            "light yellow": "#FFFFE0",
            "dark green": "#006400",
            "dark blue": "#00008B",
            "dark red": "#8B0000",
            "dark purple": "#4B0082",
            "dark orange": "#FF8C00",
            "green": "#22c55e",
            "blue": "#646cff",
            "red": "#ef4444",
            "purple": "#a855f7",
            "orange": "#f97316",
            "pink": "#ec4899",
            "yellow": "#eab308",
            "cyan": "#06b6d4",
            "teal": "#14b8a6",
        }
        
        for keyword, color_code in color_keywords.items():
            if "color" in last_message and keyword in last_message:
                print(f"🎨 [UI_CONTROL] Color change detected: {keyword} -> {color_code}", flush=True)
                # Send UI control event BEFORE the text response
                ui_control_event = json.dumps({
                    "type": "ui_control",
                    "data": {
                        "action": "change_theme",
                        "color": color_code
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }) + "\n\n"
                yield f"data: {ui_control_event}"
                color_changed = True
                detected_color = keyword
                
                # Add a system message to tell the AI it changed the color
                messages.append(Message(
                    role="system",
                    content=f"[SYSTEM: You have successfully changed the UI color to {keyword}. Acknowledge this change briefly and naturally in your response.]"
                ))
                break
        
        # Check for button addition request
        if ("add" in last_message or "create" in last_message) and "button" in last_message:
            # Extract button label - look for quoted text or common patterns
            button_label = "Test"  # Default
            
            # Try to find quoted text
            import re
            quotes_match = re.search(r'["\']([^"\']+)["\']', messages[-1].content)
            if quotes_match:
                button_label = quotes_match.group(1)
            # Or look for "button called X" or "button named X"
            elif match := re.search(r'button (?:called|named) (\w+)', last_message):
                button_label = match.group(1).capitalize()
            
            print(f"🔘 [UI_CONTROL] Button addition detected: {button_label}", flush=True)
            # Send UI control event to add button
            ui_control_event = json.dumps({
                "type": "ui_control",
                "data": {
                    "action": "add_button",
                    "label": button_label
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }) + "\n\n"
            yield f"data: {ui_control_event}"
            
            # Add system message
            messages.append(Message(
                role="system",
                content=f"[SYSTEM: You have successfully added a '{button_label}' button to the UI. Acknowledge this briefly in your response.]"
            ))
    
    # Send start event
    start_event = create_agui_event(EventType.START, {
        "agent": "ollama",
        "model": model
    })
    print(f"📤 [EVENT] Sending START event: {start_event[:100]}...", flush=True)
    yield start_event
    
    try:
        # Convert messages to Ollama format
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        print(f"🔵 [OLLAMA] Calling Ollama with {len(ollama_messages)} messages")
        print(f"🔵 [OLLAMA] Last message: {ollama_messages[-1] if ollama_messages else 'None'}")
        
        # Stream from Ollama
        full_response = ""
        chunk_count = 0
        stream = ollama.chat(
            model=model,
            messages=ollama_messages,
            stream=True,
        )
        
        print(f"🟢 [OLLAMA] Stream started successfully")
        
        for chunk in stream:
            chunk_count += 1
            if 'message' in chunk and 'content' in chunk['message']:
                content = chunk['message']['content']
                full_response += content
                
                if chunk_count <= 3 or chunk_count % 10 == 0:
                    print(f"📝 [CHUNK {chunk_count}] Received: {content[:50]}...")
                
                # Send text message event for each chunk
                event = create_agui_event(EventType.TEXT_MESSAGE, {
                    "content": content,
                    "delta": True,
                    "role": "assistant"
                })
                yield event
        
        print(f"✅ [STREAM] Received {chunk_count} chunks, total length: {len(full_response)}")
        
        # Send result event with full response
        result_event = create_agui_event(EventType.RESULT, {
            "content": full_response,
            "role": "assistant",
            "model": model
        })
        print(f"📤 [EVENT] Sending RESULT event with {len(full_response)} chars")
        yield result_event
        
        # Send end event
        end_event = create_agui_event(EventType.END, {
            "status": "completed",
            "message_count": len(full_response)
        })
        print(f"📤 [EVENT] Sending END event")
        yield end_event
        
    except Exception as e:
        print(f"❌ [ERROR] Exception in stream: {str(e)}")
        print(f"❌ [ERROR] Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Send error event
        error_event = create_agui_event(EventType.ERROR, {
            "error": str(e),
            "message": "Failed to generate response from Ollama"
        })
        print(f"📤 [EVENT] Sending ERROR event")
        yield error_event

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AG-UI POC Backend",
        "status": "running",
        "protocol": "AG-UI",
        "model": "mistral:latest"
    }

@app.get("/health")
async def health_check():
    """Check if Ollama is accessible"""
    try:
        # Try to list models to verify Ollama connection
        models = ollama.list()
        return {
            "status": "healthy",
            "ollama": "connected",
            "available_models": [model['name'] for model in models.get('models', [])]
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama not accessible: {str(e)}"
        )

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    AG-UI compliant chat endpoint with streaming
    Streams events using Server-Sent Events (SSE)
    """
    print(f"\n{'='*60}")
    print(f"🌐 [CHAT] Received /chat request")
    print(f"🌐 [CHAT] Messages: {len(request.messages)}")
    print(f"🌐 [CHAT] Model: {request.model}")
    for i, msg in enumerate(request.messages):
        print(f"  📨 Message {i+1}: [{msg.role}] {msg.content[:100]}...")
    print(f"{'='*60}\n")
    
    try:
        return StreamingResponse(
            stream_ollama_response(request.messages, request.model),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        print(f"❌ [CHAT] Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AG-UI POC Backend...")
    print("📡 Protocol: AG-UI")
    print("🤖 Model: Ollama (mistral:latest)")
    print("🌐 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
