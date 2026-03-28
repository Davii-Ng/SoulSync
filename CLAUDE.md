# SoulSync

## Project Overview
SoulSync is an AI-powered mental health companion for people experiencing burnout, stress, and loneliness. Voice-first experience: user speaks, AI listens, analyzes emotion, responds empathetically with natural voice, and proactively takes actions (save calendar events, suggest therapy resources).

Built for USF Hackathon Tampa 2026. Targeting 4 tracks: Oracle (human-centered AI), Google ADK Multi-Agent, ElevenLabs, Gemini API.

## Tech Stack
- Frontend: React + Vite + TypeScript, deploy on Vercel
- Backend: Python + FastAPI, deploy on Railway/Render
- Agents: Google ADK (Python) — multi-agent orchestration
- LLM: Gemini API (emotion analysis + conversational response)
- Voice Output: ElevenLabs Text-to-Speech API
- Voice Input: Web Speech API (browser-side) or Google Speech-to-Text
- Database: SQLite or in-memory (hackathon scope)
- Communication: WebSocket (real-time audio/text streaming between frontend and backend)

## Multi-Agent Architecture (Google ADK)
- Listener Agent — Voice-to-text, receives audio input, transcribes
- Core Companion Agent (Orchestrator) — Main agent, receives text + emotion data, manages conversation context, generates empathetic response via Gemini API
- Calendar Agent — Detects when user mentions events/deadlines, saves to internal calendar, fetches when needed
- Resource Agent — Detects signs user needs professional support, suggests therapists, hotlines, mindfulness exercises
- Voice Agent — Converts response text to natural voice via ElevenLabs API

Flow: User speaks → Listener → Core Companion (orchestrates, calls Calendar/Resource agents as needed) → Voice Agent → User hears


## Project Structure
soulsync/
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
│   ├── agent.py           # Test agent: analyze_emotion + suggest_resource tools
│   ├── core_companion.py  # Orchestrator agent
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

## Running Agents (Google ADK)
```powershell
# From project root (SoulSync/)
adk run multi_tool_agent     # terminal chat
adk web multi_tool_agent     # browser UI at localhost:8000
```
- `agent.py` is the ADK entry point — must define `root_agent`
- `__init__.py` must be UTF-8 encoded (not UTF-16)

## Coding Conventions
- Frontend: functional components, TypeScript strict, named exports
- Backend: snake_case, type hints where possible
- Commit format: type: description (feat:, fix:, clean:, init:, docs:)
- API keys in .env only, never commit
- All agent communication goes through Core Companion (orchestrator pattern)

## API Keys Needed (.env)
- GOOGLE_API_KEY — Gemini API
- ELEVENLABS_API_KEY — ElevenLabs TTS
- GOOGLE_CLOUD_PROJECT — Google ADK (if needed)