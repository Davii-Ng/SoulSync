# SoulSync

**An AI-powered voice journal that actually listens.**

Journaling is a powerful tool for mental health, but writing can feel like a chore when you're overwhelmed. Therapy is amazing, but it's not available at 2 AM on a Tuesday. 

We built **SoulSync** to bridge that gap. It's a voice-first companion that lets you vent, reflect, and process your emotions in real-time. You speak, it listens, figures out how you're feeling, and responds just like a supportive friend—while automatically saving your thoughts to a private journal. 

> Built with love for the USF Hackathon Tampa 2026.

## How it works

SoulSync is built around a real-time conversation loop. You just talk to it, and the system handles the rest.

* **🗣️ Voice-first input:** Your browser captures your words as you speak.
* **🧠 Emotion detection:** Gemini analyzes the transcript (noting mixed feelings, severity, and even crisis phrases).
* **🤝 Empathetic response:** Specialized ADK agents craft a response tailored to your mood.
* **🎧 Natural audio:** ElevenLabs voices read the response back to you.
* **📓 Auto-journaling:** Mention you want to "save the journal", and it snapshots your session.

### The Flow

```text
[You Speak] ---> (Frontend/React) ---> WS msg ---> (FastAPI/Backend)
                                                         |
                                                  [Google ADK Orchestrator]
                                                         |
 ┌───────────────┬─────────────────┬─────────────────────┼─────────────────┐
(Core Companion) (Journal Agent) (Calendar Agent) (Resource Agent)      (Voice TTS)
 Emotion/Coping  Saves/Prompts   Extracts Events   Crisis/Therapy      ElevenLabs
```

## Features

- **8-Axis Emotion Tracking**: Recognizes calm, stressed, anxious, happy, sad, angry, neutral, and crisis states. It's negation-aware (saying "I am not angry" won't flag as angry).
- **Proactive Wellness**: Detects when you're stressed and highlights built-in grounding or breathing exercises.
- **Smart Calendar Extraction**: Casually mention "I have a meeting tomorrow at 2pm" and it automatically pulls into your events board.
- **Immediate Crisis Support**: Hardcoded triggers route immediately to 988 and therapy resources if self-harm or deep crisis is detected.
- **Multi-Voice Personalization**: Choose between different ElevenLabs voices directly in the UI.

---

## Tech Stack

- 🖥️ Frontend: React + Vite + TypeScript
- ⚡ Backend: Python + FastAPI + WebSocket
- 🤖 Agents: Google ADK multi-agent
- 🧠 LLM: Gemini API (`gemini-3-flash-preview`)
- 🔊 Voice: ElevenLabs TTS + Web Speech API
- 🧳 Storage: In-memory + localStorage

---

## Quick Start

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

## API (Quick View)

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

## Tests

```bash
pip install pytest pytest-asyncio httpx
pytest -q
```

---

## Contributing

We keep contributor docs separate to keep this README lightweight.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup details, repo structure, and workflow.

---

## Hackathon Tracks

| Track | How We Use It |
|-------|--------------|
| 🧑‍⚕️ Oracle | Human-centered AI — empathetic, proactive support |
| 🧭 Google ADK | Multi-agent orchestration |
| 🗣️ ElevenLabs | Natural voice I/O |
| ✨ Gemini API | Emotion analysis + conversation |