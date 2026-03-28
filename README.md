# SoulSync

**AI-Powered Mental Health Companion for Burnout, Stress & Loneliness**

> Built with love at USF Hackathon Tampa 2026.

---

## What is SoulSync?

SoulSync is a **voice-first** AI companion that listens to you, understands your emotions, and responds with empathy — using natural voice. It proactively helps by saving calendar events, suggesting therapy resources, and guiding you through mindfulness exercises.

**You speak. SoulSync listens. You feel heard.**

---

## Hackathon Tracks

| Track | How We Use It |
|-------|--------------|
| **Oracle** | Human-centered AI — empathetic, proactive mental health support |
| **Google ADK Multi-Agent** | Multi-agent orchestration with specialized sub-agents |
| **ElevenLabs** | Natural voice output via Text-to-Speech API |
| **Gemini API** | Emotion analysis + conversational AI responses |

---

## Architecture

```
User speaks
    │
    ▼
┌──────────────────────────────────────────┐
│         root_agent (Orchestrator)         │  ← agent.py — ADK entry point
│                                           │
│  1. transcribe_audio (Listener stub)      │
│  2. delegate to core_companion sub-agent  │
│  3. manage_calendar (Calendar stub)       │
│  4. speak_response (Voice stub)           │
└───────────────┬──────────────────────────┘
                │ sub_agent
                ▼
┌──────────────────────────────────────────┐
│         core_companion_agent              │  ← Gemini: emotion analysis + response
│                                           │
│  tools: analyze_emotion, suggest_resource │
│  delegates to: calendar_agent             │
│               resource_agent              │
└──────────────────────────────────────────┘
                │
                ▼
┌──────────────────┐    ┌──────────────────┐
│  calendar_agent  │    │  resource_agent  │
│  save_event      │    │  crisis hotlines │
│  list_events     │    │  therapist refs  │
│                  │    │  mindfulness     │
└──────────────────┘    └──────────────────┘
                │
                ▼
┌──────────────────┐
│   voice_agent    │  ← ElevenLabs TTS → natural voice
│  speak_response  │
└──────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React + Vite + TypeScript |
| **Backend** | Python + FastAPI |
| **Agents** | Google ADK (Python) |
| **LLM** | Gemini API (`gemini-3-flash-preview`) |
| **Voice Output** | ElevenLabs TTS |
| **Voice Input** | Web Speech API (browser-side) |
| **Database** | SQLite / in-memory |
| **Real-time** | WebSocket |
| **Deploy** | Vercel (frontend) · Railway/Render (backend) |

---

## Project Structure

```
SoulSync/
├── frontend/                  # React + Vite + TypeScript
│   └── src/
│       ├── App.tsx
│       ├── components/
│       ├── hooks/
│       ├── types/
│       └── utils/
├── backend/                   # FastAPI entry point + WebSocket
│   └── main.py
├── multi_tool_agent/          # Google ADK agents (adk run target)
│   ├── agent.py               # ADK entry point — root_agent (main orchestrator)
│   ├── core_companion.py      # Core Companion sub-agent (emotion + response)
│   ├── calendar_agent.py      # Calendar/event management
│   ├── resource_agent.py      # Mental health resources + crisis hotlines
│   ├── listener_agent.py      # Voice-to-text (stub → Google STT)
│   ├── voice_agent.py         # Text-to-voice via ElevenLabs
│   ├── __init__.py
│   └── CLAUDE.md
├── .env                       # API keys (never commit!)
├── requirements.txt
├── CLAUDE.md
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- API keys (see below)

### 1. Clone the repo

```bash
git clone https://github.com/<your-org>/soulsync.git
cd soulsync
```

### 2. Set up environment variables

```env
GOOGLE_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project_id  # if needed
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the agents (Google ADK)

```powershell
# From project root (SoulSync/)
adk run multi_tool_agent     # terminal chat
adk web multi_tool_agent     # browser UI at localhost:8000
```

### 5. Start the backend

```bash
cd backend
uvicorn main:app --reload
# → http://localhost:8000
```

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```
