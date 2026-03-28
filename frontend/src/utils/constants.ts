// App-wide constants: WebSocket URL, emotion display config

export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export const EMOTION_CONFIG: Record<string, { label: string; color: string }> = {
  calm: { label: 'Calm', color: 'text-teal-400' },
  stressed: { label: 'Stressed', color: 'text-orange-400' },
  anxious: { label: 'Anxious', color: 'text-yellow-400' },
  happy: { label: 'Happy', color: 'text-green-400' },
  sad: { label: 'Sad', color: 'text-blue-400' },
  angry: { label: 'Angry', color: 'text-red-400' },
  neutral: { label: 'Neutral', color: 'text-gray-400' },
}