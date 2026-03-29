# SoulSync Backend

Python + FastAPI backend that serves as the API integration layer between the frontend and external AI services (Google Gemini, ElevenLabs).

## Features

- **Chat endpoint** (`POST /chat`) — Sends user messages to Google Gemini, returns an empathetic response with detected emotion.
- **Speech endpoint** (`POST /speech`) — Converts text to natural speech audio via ElevenLabs TTS. Returns `audio/mpeg` bytes.
- **WebSocket** (`WS /ws`) — Real-time conversation gateway. Accepts user text, returns AI response + emotion + base64 TTS audio in a single message.
- **Health check** (`GET /`) — Returns service status and version.
- Centralized error handling, CORS configuration, and structured JSON responses.

## Prerequisites

- Python 3.11+
- A `.env` file in the project root (or `backend/` directory) with:

```
GOOGLE_API_KEY=your-gemini-key
ELEVENLABS_API_KEY=your-elevenlabs-key
```

Optional variables:

```
GOOGLE_CLOUD_PROJECT=your-project
APP_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
REQUEST_TIMEOUT_SECONDS=20
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

## Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## API Overview

| Method | Path | Description |
|--------|---------|--------------------------------------|
| GET | `/` | Health check |
| POST | `/chat` | Send a message, get AI response |
| POST | `/speech` | Convert text to speech audio |
| WS | `/ws` | Real-time conversation via WebSocket |

## Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest -q
```
