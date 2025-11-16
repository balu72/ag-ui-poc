# AG-UI POC - Agent-User Interaction Protocol

A proof-of-concept application demonstrating the **AG-UI protocol** for agent-user interaction, connecting a React frontend with a Python (FastAPI) backend integrated with locally running Ollama (mistral:latest).

## 🏗️ Architecture

```
┌─────────────────┐      AG-UI Protocol       ┌──────────────────┐
│  React Frontend │ ◄────────────────────────► │ FastAPI Backend  │
│  (CopilotKit)   │     (HTTP/SSE Stream)      │   (AG-UI Events) │
└─────────────────┘                            └──────────────────┘
                                                         │
                                                         ▼
                                                ┌──────────────────┐
                                                │      Ollama      │
                                                │  (mistral:latest)│
                                                └──────────────────┘
```

## ✨ Features

- 🔄 **Real-time streaming** responses from AI
- 📡 **AG-UI protocol** implementation
- 🤖 **Ollama integration** with Mistral model
- ⚡ **FastAPI backend** with async support
- ⚛️ **React frontend** with TypeScript
- 🎨 **Modern UI** with CopilotKit
- 💬 **Interactive chat** interface

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Backend Requirements
- **Python 3.10+**
- **Ollama** with mistral:latest model

### Frontend Requirements
- **Node.js 18+**
- **npm** or **pnpm**

## 🚀 Quick Start

### 1. Install Ollama and Pull Mistral Model

**macOS:**
```bash
brew install ollama
ollama serve  # In a separate terminal
ollama pull mistral:latest
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull mistral:latest
```

### 2. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

Backend will be available at: **http://localhost:8000**

### 3. Setup Frontend

```bash
# Open a new terminal
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## 🎯 Usage

1. **Open your browser** and navigate to `http://localhost:5173`
2. **Click the chat icon** in the sidebar (opens by default)
3. **Start chatting** with the AI assistant powered by Ollama's Mistral model
4. **Experience real-time streaming** as the AI responds

## 📁 Project Structure

```
AG-UI-POC/
├── backend/
│   ├── main.py              # FastAPI server with AG-UI protocol
│   ├── requirements.txt     # Python dependencies
│   └── README.md           # Backend documentation
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── App.css         # Application styles
│   │   ├── main.tsx        # Entry point
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.ts      # Vite configuration
│   ├── tsconfig.json       # TypeScript config
│   └── README.md          # Frontend documentation
│
└── README.md              # This file
```

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Ollama** - Local LLM runtime
- **Mistral** - AI language model
- **Uvicorn** - ASGI server
- **Python 3.10+**

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **CopilotKit** - AG-UI protocol client
- **CSS3** - Styling

### Protocol
- **AG-UI** - Agent-User Interaction Protocol
- **SSE** - Server-Sent Events for streaming
- **HTTP** - REST API communication

## 📡 AG-UI Protocol Implementation

This POC implements the AG-UI protocol with the following event types:

### Backend Events (Server → Client)
- `START` - Agent execution started
- `TEXT_MESSAGE` - Streaming text chunks
- `RESULT` - Final complete response
- `END` - Agent execution completed
- `ERROR` - Error during execution

### Example Event Flow
```
1. Client sends message → Backend
2. Backend emits START event
3. Backend streams TEXT_MESSAGE events (real-time)
4. Backend emits RESULT event (complete response)
5. Backend emits END event
```

## 🧪 Testing the API

You can test the backend API directly:

```bash
# Health check
curl http://localhost:8000/health

# Chat request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Tell me a joke"}
    ]
  }'
```

## 🐛 Troubleshooting

### Ollama Issues
- **Error: "Ollama not accessible"**
  - Make sure Ollama is running: `ollama serve`
  - Verify the model is installed: `ollama list`
  - Pull the model if missing: `ollama pull mistral:latest`

### Backend Issues
- **Port 8000 already in use**
  - Change the port in `backend/main.py`
  - Update frontend's `runtimeUrl` in `App.tsx`

### Frontend Issues
- **Port 5173 already in use**
  - Vite will automatically try the next available port
  - Check the terminal output for the actual port
- **Backend connection error**
  - Ensure backend is running at `http://localhost:8000`
  - Check CORS configuration in `main.py`

### TypeScript Errors
- Run `npm install` to ensure all dependencies are installed
- These are IDE warnings and won't affect the runtime

## 🔗 API Endpoints

### Backend Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Ollama connection status |
| POST | `/chat` | AG-UI chat endpoint (SSE) |
| POST | `/v1/copilotkit` | CopilotKit compatible endpoint |

## 📚 Documentation

- **AG-UI Protocol**: https://github.com/ag-ui-protocol/ag-ui
- **CopilotKit**: https://docs.copilotkit.ai
- **Ollama**: https://ollama.ai/
- **FastAPI**: https://fastapi.tiangolo.com/

## 🤝 Contributing

This is a POC project. Feel free to:
- Report issues
- Suggest improvements
- Fork and experiment
- Share feedback

## 📝 License

MIT License - feel free to use this POC as a starting point for your projects.

## 🙏 Acknowledgments

- **AG-UI Protocol** team for the excellent protocol specification
- **CopilotKit** for the React client implementation
- **Ollama** team for making LLMs accessible locally
- **FastAPI** for the amazing Python framework

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review individual README files in backend/ and frontend/
3. Consult the AG-UI documentation

---

**Built with ❤️ using AG-UI Protocol**
