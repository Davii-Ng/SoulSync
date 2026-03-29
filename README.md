# SoulSync

**AI-Powered Journal & Mental Health Companion**

> Built with love at USF Hackathon Tampa 2026.

---

## What is SoulSync?

SoulSync is a **voice-first AI journal** that listens to you, understands your emotions, and responds like a friend — not a chatbot. Write or speak your thoughts, and SoulSync helps you process them, reflect on past entries, and feel less alone.

**You speak. SoulSync listens. You feel heard.**

---

## Hackathon Tracks

| Track | How We Use It |
|-------|--------------|
| **Oracle** | Human-centered AI — empathetic, proactive mental health support |
| **Google ADK Multi-Agent** | Multi-agent orchestration with 5 specialized sub-agents |
| **ElevenLabs** | Natural voice I/O — TTS via SDK + STT via Scribe MCP |
| **Gemini API** | Emotion analysis + conversational AI responses |

---

## Architecture

```
User speaks into mic (browser)
    │
    ▼  Web Speech API or base64 audio
┌─────────────────────────────────────────────────┐
│              Frontend (React + Vite)              │
│  VoiceOrb → useVoiceInput → useWebSocket         │
└───────────────────┬─────────────────────────────┘
                    │  WebSocket (ws://localhost:8000/ws)
                    ▼
┌─────────────────────────────────────────────────┐
│          Backend (FastAPI + WebSocket)            │
│  /chat  /speech  /transcribe  /ws                │
└───────────────────┬─────────────────────────────┘
                    │  Calls agent tools directly
                    ▼
┌─────────────────────────────────────────────────┐
│       root_agent (ADK Orchestrator)              │
│                                                   │
│  sub_agents:                                      │
│  ├── core_companion  → analyze_emotion,           │
│  │                     suggest_resource            │
│  ├── calendar_agent  → save_event, get_events     │
│  ├── resource_agent  → crisis hotlines,           │
│  │                     therapist refs, mindfulness │
│  ├── listener_agent  → ElevenLabs Scribe STT      │
│  │                     (via MCP toolset)           │
│  └── voice_agent     → ElevenLabs TTS             │
│                        (speak_response,            │
│                         text_to_speech)            │
└─────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React + Vite + TypeScript |
| **Backend** | Python + FastAPI + Uvicorn |
| **Agents** | Google ADK (Python) — multi-agent orchestration |
| **LLM** | Gemini API (`gemini-3-flash-preview`) |
| **Voice Output** | ElevenLabs TTS (Python SDK) |
| **Voice Input** | Web Speech API (browser) + ElevenLabs Scribe STT (server) |
| **Real-time** | WebSocket — text + audio + emotion in a single message |
| **Deploy** | Vercel (frontend) · Railway/Render (backend) |

---

## Project Structure

```
SoulSync/
├── frontend/                  # React + Vite + TypeScript
│   └── src/
│       ├── App.tsx            # Root — orb, transcript, emotion badge
│       ├── components/
│       │   ├── VoiceOrb.tsx   # Mic button with listening/thinking states
│       │   ├── ChatTranscript.tsx
│       │   ├── MessageBubble.tsx
│       │   ├── EmotionBadge.tsx
│       │   └── Header.tsx
│       ├── hooks/
│       │   ├── useWebSocket.ts   # WS connection to backend
│       │   └── useVoiceInput.ts  # Browser speech recognition
│       ├── types/
│       └── utils/
├── backend/                   # FastAPI — API integration layer
│   ├── main.py                # App entry, CORS, router registration
│   └── app/
│       ├── api/routes/
│       │   ├── health.py      # GET /
│       │   ├── chat.py        # POST /chat
│       │   ├── speech.py      # POST /speech + POST /transcribe
│       │   └── ws.py          # WS /ws — real-time conversation
│       ├── core/              # Config, CORS, security
│       ├── schemas/           # Pydantic request/response models
│       ├── ws/                # WebSocket manager + protocol
│       └── utils/             # Error handling
├── multi_tool_agent/          # Google ADK agents
│   ├── agent.py               # ADK entry point — root_agent orchestrator
│   ├── core_companion.py      # Emotion analysis + empathetic response
│   ├── calendar_agent.py      # Event detection + in-memory calendar
│   ├── resource_agent.py      # Crisis resources + therapist referrals
│   ├── listener_agent.py      # STT via ElevenLabs Scribe MCP
│   ├── voice_agent.py         # TTS via ElevenLabs SDK
│   └── __init__.py
├── tests/                     # pytest tests
├── .env                       # API keys (never commit!)
└── README.md
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check — returns status and version |
| POST | `/chat` | Send text, get AI response + detected emotion |
| POST | `/speech` | Convert text to speech, returns `audio/mpeg` bytes |
| POST | `/transcribe` | Convert base64 audio to text via ElevenLabs Scribe |
| WS | `/ws` | Real-time conversation — text or audio in, AI response + emotion + TTS audio out |

### WebSocket Protocol (`/ws`)

**Send (client → server):**
```json
{ "type": "text", "content": "I feel so burned out" }
{ "type": "audio", "content": "<base64-encoded-audio>" }
```

**Receive (server → client):**
```json
{ "type": "transcript", "content": "transcribed text" }
{ "type": "response", "content": "AI reply", "emotion": "burnout", "audio_base64": "..." }
{ "type": "error", "content": "error message" }
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys (see below)

### 1. Clone the repo

```bash
git clone https://github.com/Davii-Ng/SoulSync.git
cd SoulSync
```

### 2. Set up environment variables

Create a `.env` file in the project root:

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Optional:

```env
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
CORS_ORIGINS=http://localhost:5173
```

### 3. Install Python dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Start the backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000
# → Swagger docs at http://localhost:8000/docs
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 6. (Optional) Run agents standalone via ADK

```powershell
# From project root (SoulSync/)
adk run multi_tool_agent     # terminal chat
adk web multi_tool_agent     # browser UI at localhost:8000
```

---

## Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest -q
```

---

## Demo Walkthrough

1. Open `http://localhost:5173` in Chrome (required for Web Speech API).
2. Click the **voice orb** to start speaking.
3. Say something like _"I've been feeling really burned out lately"_.
4. Click the orb again to stop — your message appears in the transcript.
5. SoulSync analyzes your emotion, responds empathetically, and speaks the reply aloud.
6. The **emotion badge** updates to reflect the detected mood (burnout, stress, loneliness, neutral).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Mic not working | Use Chrome — Web Speech API requires it. Allow mic permission when prompted. |
| No AI response | Check that `GOOGLE_API_KEY` is set in `.env` and the backend is running. |
| No voice output | Check that `ELEVENLABS_API_KEY` is set. Verify at `http://localhost:8000/docs` → POST `/speech`. |
| WebSocket disconnect | Ensure backend is running on port 8000. Check browser console for connection errors. |
| `adk run` fails | Run from project root (`SoulSync/`), not from inside `multi_tool_agent/`. |
