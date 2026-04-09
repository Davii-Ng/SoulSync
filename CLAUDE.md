# SoulSync

## Project Overview
SoulSync is an AI-powered journal and mental health companion. Voice-first experience: user speaks or writes, AI listens, analyzes emotion, responds like a friend, saves journal entries, and proactively offers reflective prompts, coping tips, and crisis resources when needed.

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
    ├── journal_agent          ← save entries, retrieve past entries, journaling prompts
    │   └── tools: write_entry, get_entries, get_prompt
    ├── calendar_agent         ← event/deadline management (in-memory)
    │   └── tools: save_event, get_events
    └── resource_agent         ← crisis support + therapy resources
        └── tools: get_crisis_resources, get_therapist_resources, get_mindfulness_exercise

voice_agent (voice_agent.py)
└── synthesize_speech()  ← ElevenLabs TTS utility, called by backend directly
```

### Agent Definitions
- `agent.py` — ADK entry point. `root_agent` is a pure orchestrator — no direct tools, delegates everything via sub_agents.
- `core_companion.py` — Reads what the user wrote and tunes into how they're feeling. Tools: `analyze_emotion` (crisis detection, negation awareness, dynamic severity, mixed emotions), `suggest_resource` (coping tip + follow-up question per emotion).
- `journal_agent.py` — The core of the app. Saves every entry, retrieves past entries to reflect on, and offers emotion-specific journaling prompts. Tools: `write_entry`, `get_entries`, `get_prompt`.
- `calendar_agent.py` — Detects event/deadline mentions, saves to in-memory store, fetches on request. Tools: `save_event`, `get_events`.
- `resource_agent.py` — Steps in when someone is really struggling. Crisis hotlines, therapy referrals, mindfulness exercises. Tools: `get_crisis_resources`, `get_therapist_resources`, `get_mindfulness_exercise`.
- `voice_agent.py` — Exports `synthesize_speech()` utility for ElevenLabs TTS. Called by backend after agent response, not wired as sub_agent.

### ADK Rules
- `Agent` instances must go in `sub_agents`, not `tools` — `tools` only accepts callables/BaseTool/BaseToolset
- `agent.py` must define `root_agent` (ADK entry point)
- `__init__.py` must be UTF-8 encoded (not UTF-16)

### Emotion Labels
`calm | stressed | anxious | happy | sad | angry | neutral | crisis`

### Emotion Detection (core_companion.py)
- Crisis phrases checked first — returns `emotion: "crisis", severity: "critical"` if matched
- Negation-aware — "I'm not angry" won't match angry
- Dynamic severity from keyword count: 1 = low, 2-3 = medium, 4+ = high
- Returns top 2 emotions (primary + secondary) for mixed emotion support

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
│       ├── pages/         # SpeakingPage, JournalPage, CalendarPage, HistoryPage, ResourcesPage, SettingsPage
│       ├── hooks/
│       ├── types/
│       └── utils/
├── backend/               # FastAPI + WebSocket
│   └── main.py
├── multi_tool_agent/      # Google ADK agent definitions (adk run target)
│   ├── agent.py           # ADK entry point — root_agent (orchestrator)
│   ├── core_companion.py  # Emotion analysis + empathetic response
│   ├── journal_agent.py   # Journal entries + reflective prompts
│   ├── calendar_agent.py  # Event/deadline management (in-memory)
│   ├── resource_agent.py  # Crisis hotlines + therapy resources
│   ├── voice_agent.py     # ElevenLabs TTS utility (synthesize_speech)
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
