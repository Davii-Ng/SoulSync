# 🧠 SoulSync

**AI-Powered Mental Health Companion for Burnout, Stress & Loneliness**

> Built with ❤️ at USF Hackathon Tampa 2026.

---

## 💡 What is SoulSync?

SoulSync is a **voice-first** AI companion that listens to you, understands your emotions, and responds with empathy — using natural voice. It can proactively help by saving calendar events, suggesting therapy resources, and guiding you through mindfulness exercises.

**You speak. SoulSync listens. You feel heard.**

---

## 🏆 Hackathon Tracks

| Track | How We Use It |
|-------|--------------|
| **Oracle** | Human-centered AI — empathetic, proactive mental health support |
| **Google ADK Multi-Agent** | Multi-agent orchestration with specialized agents |
| **ElevenLabs** | Natural voice output via Text-to-Speech API |
| **Gemini API** | Emotion analysis + conversational AI responses |

---

## 🏗️ Architecture

```
User speaks
    │
    ▼
┌─────────────────┐
│  Listener Agent  │  ← Web Speech API (browser) → text
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Core Companion (Orchestrator)  │  ← Gemini API: emotion analysis + response
│                                 │
│   ┌──────────────┐  ┌────────────────┐
│   │ Calendar Agent│  │ Resource Agent  │
│   │ (events/     │  │ (therapists,   │
│   │  deadlines)  │  │  hotlines,     │
│   └──────────────┘  │  mindfulness)  │
│                      └────────────────┘
└────────────┬────────────────┘
             │
             ▼
┌─────────────────┐
│   Voice Agent   │  ← ElevenLabs TTS → natural voice
└────────┬────────┘
         │
         ▼
    User hears response
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React + Vite + TypeScript |
| **Backend** | Python + FastAPI |
| **Agents** | Google ADK (Python) |
| **LLM** | Gemini API |
| **Voice Output** | ElevenLabs TTS |
| **Voice Input** | Web Speech API (browser-side) |
| **Database** | SQLite / in-memory |
| **Real-time** | WebSocket |
| **Deploy** | Vercel (frontend) · Railway/Render (backend) |

---

## 📁 Project Structure

```
soulsync/
├── frontend/              # React + Vite + TypeScript
│   └── src/
├── backend/               # FastAPI entry point + WebSocket
│   ├── main.py
│   └── requirements.txt
├── agents/                # Google ADK agent definitions
│   ├── core_companion.py  # Orchestrator agent
│   ├── calendar_agent.py  # Calendar/event management
│   ├── resource_agent.py  # Mental health resources
│   ├── listener_agent.py  # Voice-to-text processing
│   └── voice_agent.py     # ElevenLabs TTS
├── .env                   # API keys (never commit!)
├── CLAUDE.md
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- API keys (see below)

### 1. Clone the repo

```bash
git clone https://github.com/<your-org>/soulsync.git
cd soulsync
```

### 2. Set up environment variables

Fill in your `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project_id  # if needed
```

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```
---


