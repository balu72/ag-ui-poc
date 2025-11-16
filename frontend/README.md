# AG-UI POC Frontend

React frontend application with CopilotKit integration implementing the AG-UI protocol.

## Prerequisites

- **Node.js 18+** installed
- **npm** or **pnpm** package manager

## Setup

1. **Install Dependencies**

```bash
cd frontend
npm install
```

Or using pnpm:
```bash
pnpm install
```

## Running the Frontend

```bash
npm run dev
```

The application will start at: **http://localhost:5173**

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx          # Main application with CopilotKit setup
│   ├── App.css          # Application styles
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.ts       # Vite configuration
└── tsconfig.json        # TypeScript configuration
```

## AG-UI Integration

This frontend uses **CopilotKit** as the AG-UI protocol client:

### Key Components

1. **CopilotKit Provider** (`App.tsx`)
   - Connects to backend at `http://localhost:8000/v1/copilotkit`
   - Handles AG-UI protocol communication
   - Manages streaming responses

2. **CopilotSidebar** (`App.tsx`)
   - Chat interface component
   - Real-time message streaming
   - Handles user input

### Backend Connection

The frontend connects to the FastAPI backend via:
```typescript
<CopilotKit
  runtimeUrl="http://localhost:8000/v1/copilotkit"
  agent="ollama_agent"
>
```

## Features

- ✅ **Real-time Chat**: Interactive chat with AI agent
- ✅ **Streaming Responses**: Live streaming of AI responses
- ✅ **AG-UI Protocol**: Full protocol compliance
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Dark/Light Mode**: Automatic theme detection

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Troubleshooting

### Port already in use
If port 5173 is already in use, Vite will automatically try the next available port (5174, 5175, etc.)

### Backend connection error
Make sure the backend is running at `http://localhost:8000`

### CopilotKit not loading
Clear browser cache and restart the dev server

## Environment Variables

You can create a `.env` file for custom configuration:

```env
VITE_API_URL=http://localhost:8000
```

Then update the `runtimeUrl` in `App.tsx`:
```typescript
runtimeUrl={import.meta.env.VITE_API_URL + "/v1/copilotkit"}
```

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

To preview the production build:
```bash
npm run preview
```

## Technologies Used

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **CopilotKit** - AG-UI client library
- **CSS3** - Styling
