# SoulSync Backend Playbook (No Database)

This file defines the backend engineering standard for SoulSync.
All backend work should follow these instructions.

## 1) Mission

The backend is a secure API integration layer between frontend and external AI services.

Primary purpose:

- Receive requests from frontend
- Call external APIs using server-side keys
- Return structured responses back to frontend

This backend is stateless for now.
No database is required.

## 2) Core Stack

- Python + FastAPI
- Uvicorn
- WebSocket for realtime messages
- python-dotenv for environment loading
- requests or httpx for outbound API calls

## 3) Required Environment Variables

Load all variables from the project root .env via python-dotenv.
Never hardcode keys or secrets.

Required:

- GOOGLE_API_KEY
- ELEVENLABS_API_KEY
- GOOGLE_CLOUD_PROJECT

Recommended:

- APP_ENV=development
- LOG_LEVEL=INFO
- CORS_ORIGINS=http://localhost:5173
- REQUEST_TIMEOUT_SECONDS=20

Startup validation rules:

- Fail fast if GOOGLE_API_KEY is missing.
- Fail fast if ELEVENLABS_API_KEY is missing.
- Warn if GOOGLE_CLOUD_PROJECT is missing unless a route requires it.

## 4) Optimized Project Structure

Use this structure to keep API-key integration code clean and maintainable:

```text
backend/
	main.py
	requirements.txt
	app/
		__init__.py
		core/
			__init__.py
			config.py            # env loading + validation
			logging.py           # app logger setup
			security.py          # CORS + request hardening
		api/
			__init__.py
			routes/
				__init__.py
				health.py          # GET /
				chat.py            # POST /chat (Gemini proxy)
				speech.py          # POST /speech (ElevenLabs proxy)
				ws.py              # WS /ws realtime gateway
		services/
			__init__.py
			llm_service.py       # Google API calls
			tts_service.py       # ElevenLabs API calls
			orchestrator.py      # optional routing logic to agents
		ws/
			__init__.py
			manager.py           # websocket connection manager
		schemas/
			__init__.py
			chat.py
			speech.py
			common.py
		utils/
			__init__.py
			errors.py
			ids.py
			time.py
	tests/
		test_health.py
		test_chat.py
		test_speech.py
		test_ws.py
```

## 5) Backend Coding Rules

- Use snake_case in all Python files.
- Add type hints for all functions and methods.
- Keep endpoints thin; put provider logic in services.
- Use pydantic schemas for all inputs/outputs.
- Never expose raw provider errors directly to frontend.
- Do not store user data server-side unless explicitly requested later.

## 6) API and WebSocket Contracts

Health endpoint:

- GET /
- Returns service status and version.

Chat proxy endpoint:

- POST /chat
- Takes user message and optional context.
- Calls Google provider with GOOGLE_API_KEY.
- Returns normalized assistant text payload.

Speech proxy endpoint:

- POST /speech
- Takes assistant text.
- Calls ElevenLabs with ELEVENLABS_API_KEY.
- Returns audio bytes, stream, or signed URL metadata.

Realtime endpoint:

- WS /ws
- Receives user events, returns status and assistant events.

Recommended response envelope:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "uuid"
}
```

Recommended websocket envelope:

```json
{
  "type": "user_message|assistant_message|status|error",
  "timestamp": "2026-03-28T00:00:00Z",
  "payload": {}
}
```

## 7) Request Flow (Stateless)

1. Frontend sends user input to backend (REST or WS).
2. Backend validates input with pydantic.
3. Backend calls external provider using server-side API keys.
4. Backend normalizes provider response.
5. Backend returns standardized response to frontend.

No persistence step is required.

## 8) Performance and Reliability

- Use async endpoints for I/O-heavy API calls.
- Reuse outbound HTTP clients.
- Add timeout, retry, and fallback behavior for provider calls.
- Handle WebSocket disconnect cleanly.
- Add lightweight rate limiting to protect API keys.
- Keep payload sizes bounded to avoid abuse.

## 9) Security and Privacy

- Never expose API keys to frontend code.
- Never return secrets in responses.
- Never log full auth headers or secret values.
- Restrict CORS to trusted frontend origins.
- Validate and sanitize client payloads.
- Use centralized error handling with safe messages.

Recommended .gitignore entries:

```gitignore
.env
__pycache__/
```

## 10) Testing Standard

Minimum tests:

- GET / returns 200.
- POST /chat returns normalized response shape.
- POST /speech handles valid and invalid payloads.
- WS /ws accepts connection and returns status/error safely.
- Missing GOOGLE_API_KEY fails startup.
- Missing ELEVENLABS_API_KEY fails startup.

Recommended tooling:

- pytest
- pytest-asyncio
- httpx

## 11) Local Setup and Run

From backend directory:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Run tests:

```bash
pytest -q
```

## 12) Deployment Baseline (Railway or Render)

- Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
- Configure all environment variables in deployment dashboard.
- Keep frontend and backend on separate origins with strict CORS.
- Use provider timeout and retry settings suitable for production.
- Pin Python version for consistent builds.

## 13) Definition of Done

A backend task is complete only when:

- endpoints and ws contracts are stable,
- environment variables are validated,
- provider calls are secure and reliable,
- tests pass,
- no secret exposure exists in code or logs.

## 14) Boundary with Agents

backend/ is the API integration and transport layer.
agents/ contains AI behavior and orchestration logic when needed.

Backend should connect frontend to providers safely.
It should remain stateless unless persistence is explicitly introduced later.
