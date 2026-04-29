# SoulSync

**AI-Powered Journal & Mental Health Companion**

> Built with love at USF Hackathon Tampa 2026.

---

## 🌟 What is SoulSync?

SoulSync is a **voice-first AI journal** that listens to you, understands your emotions, and responds like a supportive friend. Speak or type your thoughts, and SoulSync helps you reflect, track patterns, and access support when it matters most.

---

## ✨ At a Glance

| What | Why it matters |
|------|----------------|
| 🎙️ Voice-first chat | Natural, low-friction journaling |
| 🧠 Emotion detection | Understands how you feel in the moment |
| 📓 Journal autosave | Captures meaningful reflections automatically |
| 📅 Event extraction | Pulls deadlines and plans from conversation |
| 🆘 Crisis resources | Gentle, immediate support when needed |

---

## 🗺️ How It Works (Simple Diagram)

```
[You] --voice/text--> [Frontend] --WS/HTTP--> [Backend] --> [ADK Agents]
    |                     |                       |            |
    |                     |                       |            +--> Emotion + Response
    |                     |                       |            +--> Journal + Prompts
    |                     |                       |            +--> Events + Resources
    |                     |<-- audio + emotion ----+<-----------+
```

---

## 🧭 Architecture (Detailed Map)

```
User speaks (browser)
     |
     v
Frontend (React + Vite)
    - Voice orb + transcript
    - Quick check-in
    - Journal autosave
    - Voice selection
     |
     v  WebSocket + REST
Backend (FastAPI)
    - /chat /speech /transcribe /voices /ws
    - Emotion + response routing
    - Per-connection voice prefs
     |
     v
Google ADK Orchestrator
    - core_companion (emotion + coping)
    - journal_agent (entries + prompts)
    - calendar_agent (events)
    - resource_agent (crisis + resources)
```

---

## 🧠 What Makes SoulSync Special

- 🧩 **Emotion-aware responses** with mixed mood support
- 🛟 **Crisis detection** with gentle, immediate resources
- 📝 **Journal auto-save** triggered by natural phrases
- 🎧 **Voice selection + preview** powered by ElevenLabs
- 🗓️ **Event detection** for therapy, deadlines, and plans
- 🌿 **Wellness widgets** (breathing + grounding)

---

## 🧱 Tech Stack

- 🖥️ Frontend: React + Vite + TypeScript
- ⚡ Backend: Python + FastAPI + WebSocket
- 🤖 Agents: Google ADK multi-agent
- 🧠 LLM: Gemini API (`gemini-3-flash-preview`)
- 🔊 Voice: ElevenLabs TTS + Web Speech API
- 🧳 Storage: In-memory + localStorage

---

## 🚀 Quick Start

### 1) Environment

Create `.env` in the project root:

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

### 2) Run Backend

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Run Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API (Quick View)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health check |
| POST | `/chat` | Text → AI response |
| POST | `/speech` | Text → audio |
| GET | `/voices` | List voices |
| POST | `/voices/preview` | Voice preview |
| POST | `/transcribe` | Audio → text |
| WS | `/ws` | Real-time chat + audio + emotion |

---

## 🧪 Tests

```bash
pip install pytest pytest-asyncio httpx
pytest -q
```

---

## 🤝 Contributing

We keep contributor docs separate to keep this README lightweight.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup details, repo structure, and workflow.

---

## 🏁 Hackathon Tracks

| Track | How We Use It |
|-------|--------------|
| 🧑‍⚕️ Oracle | Human-centered AI — empathetic, proactive support |
| 🧭 Google ADK | Multi-agent orchestration |
| 🗣️ ElevenLabs | Natural voice I/O |
| ✨ Gemini API | Emotion analysis + conversation |