# SoulSync Frontend

## Tech
React + Vite + TypeScript. Deploy on Vercel.

## Setup
npm install
npm run dev → http://localhost:5173

## Rules
- Functional components only, no class components
- TypeScript strict mode
- Named exports (export function, not export default where possible)
- App.tsx is the root component
- Styles: index.css for global reset, component-level CSS modules or inline styles
- No App.css — deleted during cleanup

## Key Responsibilities
- Multi-page SPA with react-router-dom (Layout + bottom nav + sidebar)
- Voice input UI (mic button, recording state, waveform)
- Display conversation transcript (user + AI messages)
- Emotion indicator display
- Audio playback of AI response (from ElevenLabs)
- Voice selection and preview (Settings page)
- WebSocket connection to backend for real-time communication

## Communication with Backend
- WebSocket at ws://localhost:8000/ws (dev)
- Send: user audio/text transcription
- Receive: AI text response + audio URL/blob + emotion data + calendar events

## File Structure
src/
├── main.tsx           # Entry point
├── App.tsx            # Root — routing, global state, WebSocket wiring
├── index.css          # Global reset styles
├── components/        # Reusable UI components (Layout, VoiceOrb, ChatTranscript, etc.)
├── pages/             # Route pages (SpeakingPage, JournalPage, CalendarPage, HistoryPage, ResourcesPage, SettingsPage)
├── hooks/             # Custom hooks (useWebSocket, useVoiceInput)
├── types/             # TypeScript type definitions
└── utils/             # Helper functions

## Navigation
- Bottom nav (always visible): Speak (/), Journal (/journal), Calendar (/calendar)
- Sidebar (desktop): History (/history), Resources (/resources), Settings (/settings)
- Layout.tsx provides the app shell with header, sidebar, and bottom nav