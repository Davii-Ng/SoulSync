# SoulSync Agents

## Tech
Python + Google ADK. Agents are orchestrated by Core Companion.

## Rules
- Each agent is one file, one responsibility
- All agents communicate through Core Companion (orchestrator pattern)
- snake_case, type hints on function signatures
- API keys loaded from root .env via python-dotenv
- Never hardcode keys or secrets

## Agent Definitions
- core_companion.py — Orchestrator. Receives user text, analyzes emotion via Gemini API, generates empathetic response, delegates to other agents when needed
- listener_agent.py — Voice-to-text. Handles audio transcription
- calendar_agent.py — Detects event/deadline mentions in conversation, saves to internal store, fetches when user asks
- resource_agent.py — Detects signs user needs professional help, fetches therapy resources, hotlines, mindfulness exercises
- voice_agent.py — Text-to-voice via ElevenLabs API, returns audio to backend

## Flow
User audio → Listener Agent → text → Core Companion → (calls Calendar/Resource if needed) → response text → Voice Agent → audio back to backend

## File Structure
multi_tool_agent/
├── agent.py           # ADK entry point — defines root_agent, test tools
├── CLAUDE.md
├── core_companion.py
├── calendar_agent.py
├── resource_agent.py
├── listener_agent.py
├── voice_agent.py
└── __init__.py        # Must stay UTF-8 encoded

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