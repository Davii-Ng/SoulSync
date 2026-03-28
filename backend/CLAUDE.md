# SoulSync Backend

## Tech
Python + FastAPI. Deploy on Railway/Render.

## Setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload → http://localhost:8000

## Rules
- snake_case for all Python code
- Type hints on function signatures
- main.py is the FastAPI entry point
- API keys loaded from root .env via python-dotenv
- Never hardcode keys or secrets

## Key Responsibilities
- WebSocket endpoint /ws for real-time frontend communication
- Receive user text/audio from frontend
- Route to agents (import from ../agents/)
- Return AI response text + ElevenLabs audio + metadata to frontend
- Manage conversation session state

## Endpoints
- GET / — health check
- WS /ws — main WebSocket for real-time voice/text communication

## Dependencies
- fastapi
- uvicorn
- websockets
- python-dotenv

## Relationship with Agents
Backend imports agents from the agents/ folder at project root. Backend is the API layer, agents handle the AI logic. Backend does NOT contain agent logic — it only routes messages to/from agents.