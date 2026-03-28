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
- Voice input UI (mic button, recording state, waveform)
- Display conversation transcript (user + AI messages)
- Emotion indicator display
- Audio playback of AI response (from ElevenLabs)
- WebSocket connection to backend for real-time communication

## Communication with Backend
- WebSocket at ws://localhost:8000/ws (dev)
- Send: user audio/text transcription
- Receive: AI text response + audio URL/blob + emotion data + calendar events

## File Structure
src/
├── main.tsx           # Entry point
├── App.tsx            # Root component
├── index.css          # Global reset styles
├── components/        # Reusable UI components
├── hooks/             # Custom hooks (useWebSocket, useAudioRecorder, etc.)
├── types/             # TypeScript type definitions
└── utils/             # Helper functions