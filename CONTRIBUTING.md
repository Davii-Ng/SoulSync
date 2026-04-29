# Contributing to SoulSync

Thanks for helping build SoulSync! This guide focuses on developer setup, repo structure, and contribution flow.

---

## ✅ Prerequisites

- Python 3.11+
- Node.js 18+
- API keys (Gemini + ElevenLabs)

---

## 🧰 Local Setup

### 1) Environment

Create a `.env` in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Optional:

```env
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
CORS_ORIGINS=http://localhost:5173
APP_ENV=development
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=20
```

Frontend (optional, `frontend/.env`):

```env
VITE_WS_URL=ws://localhost:8000/ws
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Run Locally

### Backend

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🧭 Repo Structure (Quick Map)

```
backend/           FastAPI API + WebSocket
  app/api/routes   REST + WS routes
  app/services     Agent orchestration + integrations
frontend/          React UI
multi_tool_agent/  Google ADK agents
```

---

## 🧠 Core Systems & How They Work

To help you get started, here is a breakdown of the key functions and how the codebase processes information.

### 1. The Multi-Agent Orchestrator (`multi_tool_agent/`)
We use **Google ADK** to intelligently route user requests. The `agent.py` file acts as the traffic cop (`root_agent`), delegating tasks to four sub-agents:

- **`core_companion.py`**: The heart of the conversation. Modifying `analyze_emotion` here lets you change the keyword scoring for mood detection, handle mixed emotions, and tweak crisis phrase triggers.
- **`journal_agent.py`**: Manages reading/writing to the journal. Check `get_prompt` if you want to add new reflective questions based on specific moods.
- **`calendar_agent.py`**: Listens for schedule mentions and extracts dates/times.
- **`resource_agent.py`**: A fallback agent that provides 988 hotlines or parses local therapy searches.

### 2. WebSocket Gateway (`backend/app/api/routes/ws.py`)
All real-time communication flows through a single WebSocket connection. 
- **Inbound:** Frontend sends JSON like `{ "type": "text", "content": "I feel burned out" }`.
- **Processing:** The backend passes this to the ADK orchestrator. Upon resolving the LLM response, it requests ElevenLabs to synthesize the audio.
- **Outbound:** It streams back `{ "type": "response", "content": "...", "audio_base64": "...", "emotion": "stressed" }`.

*Note: If you add new event types (e.g., sending image analysis), update both `ws.py` and the frontend `useWebSocket.ts` hook.*

### 3. Frontend Audio & Logic (`frontend/src/`)
- **Voice Interfacing**: Look at `hooks/useVoiceInput.ts`. It wraps the native browser Web Speech API for dictation.
- **Storage**: To keep this hackathon project lightweight, we use React Context + `localStorage` heavily rather than a heavy database. Check `utils/constants.ts` for storage keys.

---

## 🔁 Contribution Flow

1. Create a feature branch from `main`.
2. Keep changes scoped and documented.
3. Add or update tests when behavior changes.
4. Run tests locally (see below).
5. Open a PR with a clear description.

---

## 🧪 Tests

```bash
pip install pytest pytest-asyncio httpx
pytest -q
```

---

## ✅ Conventions

- Frontend: functional components, TypeScript strict, named exports.
- Backend: snake_case, type hints where possible.
- Agents: use `gemini-3-flash-preview` for all LLM models.
- Keys live in `.env` only. Never commit secrets.

---

## 🧩 Notes for Contributors

- WebSocket contract lives in backend routes and is mirrored in frontend hooks.
- Agent orchestration is defined in `multi_tool_agent/agent.py`.
- Keep responses empathetic and supportive in agent prompts and content.
