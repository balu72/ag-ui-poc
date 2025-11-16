import { useState, useEffect, useRef } from "react";
import "./App.css";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [themeColor, setThemeColor] = useState("#646cff"); // Default blue
  const [customButtons, setCustomButtons] = useState<string[]>([]); // Dynamic buttons
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      console.log("📤 Sending message to backend:", input);
      
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          model: "mistral:latest",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log("✅ Connected to SSE stream");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";

      // Add empty assistant message that we'll update
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "" },
      ]);

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log("🏁 Stream ended");
            break;
          }

          const chunk = decoder.decode(value);
          console.log("📦 Received chunk:", chunk.substring(0, 100));

          // Parse SSE events
          const lines = chunk.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const eventData = JSON.parse(line.substring(6));
                console.log("📨 Event:", eventData.type);

                if (eventData.type === "text_message" && eventData.data.content) {
                  assistantMessage += eventData.data.content;
                  // Update the last message (assistant)
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1] = {
                      role: "assistant",
                      content: assistantMessage,
                    };
                    return newMessages;
                  });
                } else if (eventData.type === "ui_control") {
                  // Handle UI control events
                  if (eventData.data.action === "change_theme") {
                    const newColor = eventData.data.color;
                    console.log("🎨 Theme change requested:", newColor);
                    setThemeColor(newColor);
                  } else if (eventData.data.action === "add_button") {
                    const buttonLabel = eventData.data.label;
                    console.log("🔘 Button addition requested:", buttonLabel);
                    setCustomButtons((prev) => [...prev, buttonLabel]);
                  }
                }
              } catch (e) {
                console.error("Error parsing event:", e);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("❌ Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, there was an error processing your request.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-container" style={{ '--theme-color': themeColor } as React.CSSProperties}>
      <header className="app-header" style={{ borderBottomColor: themeColor }}>
        <h1 style={{ background: `linear-gradient(135deg, ${themeColor} 0%, ${themeColor}dd 100%)`, WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>🤖 AG-UI POC</h1>
        <div className="tech-stack">
          <span className="badge" style={{ background: themeColor }}>React</span>
          <span className="badge" style={{ background: themeColor }}>FastAPI</span>
          <span className="badge" style={{ background: themeColor }}>Ollama</span>
          <span className="badge" style={{ background: themeColor }}>AG-UI Protocol (Pure REST+SSE)</span>
        </div>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
            >
              <div className="message-role">
                {message.role === "user" ? "👤 You" : "🤖 Assistant"}
              </div>
              <div className="message-content">{message.content || "..."}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Press Enter to send)"
            disabled={isLoading}
            rows={3}
          />
          <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
            {isLoading ? "⏳ Streaming..." : "📤 Send"}
          </button>
        </div>
      </main>

      <footer className="app-footer">
        {customButtons.length > 0 && (
          <div className="custom-buttons" style={{ marginBottom: "1rem" }}>
            <p style={{ fontSize: "0.85rem", opacity: 0.7, marginBottom: "0.5rem" }}>
              AI-Generated Buttons:
            </p>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "center" }}>
              {customButtons.map((label, index) => (
                <button
                  key={index}
                  onClick={() => alert(`Button "${label}" clicked!`)}
                  style={{
                    background: themeColor,
                    color: "white",
                    border: "none",
                    padding: "0.5rem 1rem",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontSize: "0.9rem",
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}
        <p className="status">
          {isLoading ? "🟢 Streaming..." : "🔵 Ready"}
        </p>
      </footer>
    </div>
  );
}

export default App;
