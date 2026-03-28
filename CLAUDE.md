# SoulSync

## Project Overview
SoulSync is an AI-powered mental health companion for people experiencing burnout, stress, and loneliness. Voice-first experience: user speaks, AI listens, analyzes emotion, responds empathetically with natural voice, and proactively takes actions (save calendar events, suggest therapy resources).

Built for USF Hackathon Tampa 2026. Targeting 4 tracks: Oracle (human-centered AI), Google ADK Multi-Agent, ElevenLabs, Gemini API.

## Tech Stack
- Frontend: React + Vite + TypeScript, deploy on Vercel
- Backend: Python + FastAPI, deploy on Railway/Render
- Agents: Google ADK (Python) — multi-agent orchestration
- LLM: Gemini API (`gemini-3-flash-preview`) — emotion analysis + conversational response
- Voice Output: ElevenLabs Text-to-Speech API
- Voice Input: Web Speech API (browser-side) or Google Speech-to-Text
- Database: SQLite or in-memory (hackathon scope)
- Communication: WebSocket (real-time audio/text streaming between frontend and backend)

## Multi-Agent Architecture (Google ADK)

### Orchestration Pattern
`agent.py` defines `root_agent` — the ADK entry point and main orchestrator. It owns the full pipeline and delegates emotional support to `core_companion_agent` via `sub_agents`.

```
root_agent (agent.py)
├── tools: transcribe_audio, manage_calendar, speak_response  ← pipeline stubs
└── sub_agents: [core_companion_agent]                        ← ADK sub-agent

core_companion_agent (core_companion.py)
└── tools: analyze_emotion, suggest_resource
```

### Agent Definitions
- `agent.py` — ADK entry point. `root_agent` orchestrates the full pipeline: transcribe → companion → calendar → speak
- `core_companion.py` — Core Companion sub-agent. Emotion analysis + empathetic response via Gemini. Delegates to calendar/resource agents when needed
- `calendar_agent.py` — Detects event/deadline mentions, saves to in-memory store, fetches on request
- `resource_agent.py` — Detects severe distress, provides crisis hotlines, therapist referrals, mindfulness exercises
- `listener_agent.py` — Voice-to-text transcription (stub → Google Speech-to-Text)
- `voice_agent.py` — Text-to-voice via ElevenLabs API (stub → full integration)

### ADK Rules
- `Agent` instances must go in `sub_agents`, not `tools` — `tools` only accepts callables/BaseTool/BaseToolset
- `agent.py` must define `root_agent` (ADK entry point)
- `__init__.py` must be UTF-8 encoded (not UTF-16)

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
├── backend/               # FastAPI entry point + WebSocket
│   └── main.py
├── multi_tool_agent/      # Google ADK agent definitions (adk run target)
│   ├── agent.py           # ADK entry point — root_agent (main orchestrator)
│   ├── core_companion.py  # Core Companion sub-agent
│   ├── calendar_agent.py  # Calendar/event management
│   ├── resource_agent.py  # Mental health resources
│   ├── listener_agent.py  # Voice-to-text processing
│   ├── voice_agent.py     # ElevenLabs TTS
│   ├── __init__.py
│   └── CLAUDE.md
├── .env                   # API keys (never commit)
├── requirements.txt
├── CLAUDE.md
└── README.md
```

## Running Agents (Google ADK)
```powershell
# From project root (SoulSync/)
adk run multi_tool_agent     # terminal chat
adk web multi_tool_agent     # browser UI at localhost:8000
```

## Coding Conventions
- Frontend: functional components, TypeScript strict, named exports
- Backend: snake_case, type hints where possible
- Agents: use `gemini-3-flash-preview` for all LLM models
- Commit format: type: description (feat:, fix:, chore:, init:, docs:)
- API keys in .env only, never commit
- Agent instances go in `sub_agents`, plain functions go in `tools`

## API Keys Needed (.env)
- GOOGLE_API_KEY — Gemini API
- ELEVENLABS_API_KEY — ElevenLabs TTS
- GOOGLE_CLOUD_PROJECT — Google ADK (if needed)
