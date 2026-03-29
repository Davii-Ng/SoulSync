# SoulSync Agents

## Tech
Python + Google ADK. Multi-agent orchestration via `root_agent` in `agent.py`.

## Rules
- Each agent is one file, one responsibility
- `root_agent` (agent.py) is the ADK entry point and top-level orchestrator
- Agent instances go in `sub_agents`, plain functions go in `tools`
- snake_case, type hints on function signatures
- API keys loaded from root .env via python-dotenv
- Never hardcode keys or secrets
- Use `gemini-3-flash-preview` for all LLM models
- `__init__.py` must stay UTF-8 encoded

## Architecture

```
root_agent (agent.py) — ADK entry point, orchestrator
├── sub_agents:
│   ├── core_companion_agent (core_companion.py) — emotion analysis + empathetic response
│   │   └── tools: analyze_emotion, suggest_resource
│   ├── calendar_agent (calendar_agent.py) — event/deadline management
│   │   └── tools: save_event, list_events
│   └── resource_agent (resource_agent.py) — crisis support + therapy resources
│       └── tools: get_crisis_resources, get_therapist_resources, get_mindfulness_exercise
└── tools: [] (pure orchestrator, no direct tools)
```

### Not wired as sub_agents:
- **voice_agent.py** — Exports `synthesize_speech()` utility function for ElevenLabs TTS. Called by backend directly (post-processing), not an ADK sub_agent.
- **listener_agent.py** — Unused at runtime. Browser Web Speech API handles voice-to-text.

## Emotion Labels
Aligned with frontend types: `calm | stressed | anxious | happy | sad | angry | neutral`

## Flow
User text → root_agent → delegates to core_companion (emotion + response) → may delegate to calendar_agent or resource_agent → response text returned to backend → backend calls `synthesize_speech()` for TTS audio

## File Structure
```
multi_tool_agent/
├── agent.py           # ADK entry point — root_agent (orchestrator)
├── core_companion.py  # Emotion analysis + empathetic response
├── calendar_agent.py  # Event/deadline management (in-memory store)
├── resource_agent.py  # Crisis hotlines, therapy refs, mindfulness
├── voice_agent.py     # ElevenLabs TTS utility (synthesize_speech)
├── listener_agent.py  # Voice-to-text stub (unused — browser handles STT)
├── __init__.py        # Must stay UTF-8 encoded
└── CLAUDE.md
```

## Running
```powershell
# From SoulSync/ root
adk run multi_tool_agent
adk web multi_tool_agent
```

## Dependencies
- google-adk
- google-generativeai (Gemini)
- elevenlabs
- python-dotenv
