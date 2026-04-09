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
│   ├── journal_agent (journal_agent.py) — journal entries + reflective prompts
│   │   └── tools: write_entry, get_entries, get_prompt
│   ├── calendar_agent (calendar_agent.py) — event/deadline management
│   │   └── tools: save_event, get_events
│   └── resource_agent (resource_agent.py) — crisis support + therapy resources
│       └── tools: get_crisis_resources, get_therapist_resources, get_mindfulness_exercise
└── tools: [] (pure orchestrator)
```

### Not wired as sub_agents:
- **voice_agent.py** — Exports `synthesize_speech()` utility for ElevenLabs TTS. Called by backend directly.

## Agent Definitions

### core_companion.py
Reads what the user wrote and tunes into how they're feeling.
- `analyze_emotion(text)` — crisis detection first, then negation-aware keyword scoring, dynamic severity, returns top 2 emotions
- `suggest_resource(emotion)` — returns a coping tip + follow-up question to keep the conversation going

### journal_agent.py
The core of the app — every entry gets saved here.
- `write_entry(content, emotion)` — saves entry with timestamp
- `get_entries(date)` — retrieves past entries, optionally filtered by date
- `get_prompt(emotion)` — returns an emotion-specific reflective journaling prompt

### calendar_agent.py
Handles schedule mentions in conversation.
- `save_event(title, date, time, description)` — saves to in-memory store
- `get_events(date)` — retrieves events, optionally filtered by date

### resource_agent.py
Steps in when someone is really struggling — gently.
- `get_crisis_resources()` — 988 Lifeline, Crisis Text Line, NAMI
- `get_therapist_resources()` — Psychology Today, BetterHelp, Open Path Collective
- `get_mindfulness_exercise()` — 5-4-3-2-1 grounding technique

## Emotion Labels
`calm | stressed | anxious | happy | sad | angry | neutral | crisis`

## Emotion Detection Notes
- Crisis phrases are checked before anything else
- Negation-aware: "I'm not angry" won't match angry
- Dynamic severity from keyword count: 1=low, 2-3=medium, 4+=high
- Returns primary + secondary emotion for mixed states

## File Structure
```
multi_tool_agent/
├── agent.py           # ADK entry point — root_agent (orchestrator)
├── core_companion.py  # Emotion analysis + empathetic response
├── journal_agent.py   # Journal entries + reflective prompts
├── calendar_agent.py  # Event/deadline management (in-memory)
├── resource_agent.py  # Crisis hotlines, therapy refs, mindfulness
├── voice_agent.py     # ElevenLabs TTS utility (synthesize_speech)
├── __init__.py        # Must stay UTF-8 encoded
└── CLAUDE.md
```

## Running
```bash
# From SoulSync/ root
adk run multi_tool_agent
adk web multi_tool_agent
```

## Dependencies
- google-adk
- google-generativeai (Gemini)
- elevenlabs
- python-dotenv
