# AG-UI POC Backend

FastAPI backend with Ollama integration implementing the AG-UI protocol.

## Prerequisites

1. **Python 3.10+** installed
2. **Ollama** installed and running
3. **mistral:latest** model downloaded

### Install Ollama (if not installed)

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Download Mistral Model

```bash
ollama pull mistral:latest
```

### Start Ollama Service

```bash
ollama serve
```

## Setup

1. **Create Virtual Environment** (recommended)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

## Running the Backend

```bash
python main.py
```

The server will start at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

## API Endpoints

### `GET /`
Health check endpoint

### `GET /health`
Check if Ollama is accessible and list available models

### `POST /chat`
AG-UI compliant chat endpoint with streaming

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "model": "mistral:latest"
}
```

**Response:** Server-Sent Events (SSE) stream with AG-UI protocol events

### `POST /v1/copilotkit`
CopilotKit compatible endpoint (for frontend integration)

## AG-UI Protocol Events

The backend emits the following AG-UI protocol events:

- **START**: Agent execution started
- **TEXT_MESSAGE**: Streaming text chunks from the LLM
- **RESULT**: Final complete response
- **END**: Agent execution completed
- **ERROR**: Error occurred during execution

## Testing the API

### Using curl:

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

## Troubleshooting

### Error: "Ollama not accessible"
- Make sure Ollama is running: `ollama serve`
- Verify model is downloaded: `ollama list`

### Error: "Connection refused"
- Check if port 8000 is available
- Try running on a different port: `uvicorn main:app --port 8001`

### Model not found
- Pull the model: `ollama pull mistral:latest`
- Check available models: `ollama list`

## Environment Variables

You can create a `.env` file for configuration:

```env
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=mistral:latest
PORT=8000
```
