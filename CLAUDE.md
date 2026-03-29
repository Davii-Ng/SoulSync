# SoulSync

## Project Overview
SoulSync is an AI-powered mental health companion for people experiencing burnout, stress, and loneliness. Voice-first experience: user speaks, AI listens, analyzes emotion, responds empathetically with natural voice, and proactively takes actions (save calendar events, suggest therapy resources).

Built for USF Hackathon Tampa 2026. Targeting 4 tracks: Oracle (human-centered AI), Google ADK Multi-Agent, ElevenLabs, Gemini API.

## Tech Stack
- Frontend: React + Vite + TypeScript, deploy on Vercel
- Backend: Python + FastAPI + WebSocket, deploy on Railway/Render
- Agents: Google ADK (Python) — multi-agent orchestration
- LLM: Gemini API (`gemini-3-flash-preview`) — emotion analysis + conversational response
- Voice Output: ElevenLabs Text-to-Speech API
- Voice Input: Web Speech API (browser-side)
- Database: In-memory (hackathon scope)
- Communication: WebSocket (real-time between frontend and backend)

## Multi-Agent Architecture (Google ADK)

### Orchestration Pattern

```
root_agent (agent.py) — ADK entry point, pure orchestrator
├── tools: []
└── sub_agents:
    ├── core_companion_agent   ← emotion analysis + empathetic response
    │   └── tools: analyze_emotion, suggest_resource
    ├── calendar_agent         ← event/deadline management
    │   └── tools: save_event, list_events
    └── resource_agent         ← crisis support + therapy resources
        └── tools: get_crisis_resources, get_therapist_resources, get_mindfulness_exercise

voice_agent (voice_agent.py)
└── synthesize_speech()  ← ElevenLabs TTS utility, called by backend directly
```

### Agent Definitions
- `agent.py` — ADK entry point. `root_agent` orchestrates via sub_agents. Pure orchestrator — no direct tools.
- `core_companion.py` — Emotion analysis + empathetic response via Gemini. Tools: `analyze_emotion`, `suggest_resource`.
- `calendar_agent.py` — Detects event/deadline mentions, saves to in-memory store, fetches on request.
- `resource_agent.py` — Detects severe distress, provides crisis hotlines, therapist referrals, mindfulness exercises.
- `voice_agent.py` — Exports `synthesize_speech()` utility for ElevenLabs TTS. Called by backend after agent response, not wired as sub_agent.
- `listener_agent.py` — Unused at runtime. Browser Web Speech API handles voice-to-text.

### ADK Rules
- `Agent` instances must go in `sub_agents`, not `tools` — `tools` only accepts callables/BaseTool/BaseToolset
- `agent.py` must define `root_agent` (ADK entry point)
- `__init__.py` must be UTF-8 encoded (not UTF-16)

### Emotion Labels
Aligned with frontend types: `calm | stressed | anxious | happy | sad | angry | neutral`

### WebSocket Protocol
- **Client → Server:** `{ "type": "text", "content": "user message" }`
- **Server → Client:** `{ "content": "AI response", "emotion": "stressed", "audio_base64": "..." }`

## Project Structure
```
SoulSync/
├── frontend/              # React + Vite + TypeScript
│   └── src/
│       ├── App.tsx
│       ├── components/
│       ├── hooks/
│       ├── types/
│       └── utils/
├── backend/               # FastAPI + WebSocket
│   └── main.py
├── multi_tool_agent/      # Google ADK agent definitions (adk run target)
│   ├── agent.py           # ADK entry point — root_agent (orchestrator)
│   ├── core_companion.py  # Emotion analysis + empathetic response
│   ├── calendar_agent.py  # Event/deadline management
│   ├── resource_agent.py  # Crisis hotlines + therapy resources
│   ├── voice_agent.py     # ElevenLabs TTS utility (synthesize_speech)
│   ├── listener_agent.py  # Voice-to-text stub (unused — browser handles STT)
│   ├── __init__.py
│   └── CLAUDE.md
├── .env                   # API keys (never commit)
├── requirements.txt
├── CLAUDE.md
└── README.md
```

## Running Agents (Google ADK)
```bash
# From project root (SoulSync/)
adk run multi_tool_agent     # terminal chat
adk web multi_tool_agent     # browser UI at localhost:8000
```

## Running Backend
```bash
# From project root (SoulSync/)
python -m uvicorn backend.main:app --reload
# → http://localhost:8000
```

## Coding Conventions
- Frontend: functional components, TypeScript strict, named exports
- Backend: snake_case, type hints where possible
- Agents: use `gemini-3-flash-preview` for all LLM models
- Commit format: `type: description` (feat:, fix:, chore:, init:, docs:, refactor:)
- API keys in `.env` only, never commit
- Agent instances go in `sub_agents`, plain functions go in `tools`

## API Keys Needed (.env)
- `GOOGLE_API_KEY` — Gemini API
- `ELEVENLABS_API_KEY` — ElevenLabs TTS
- `GOOGLE_CLOUD_PROJECT` — Google ADK (if needed)
