// App-wide constants: WebSocket URL, emotion display config

export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export const EMOTION_CONFIG: Record<string, { label: string; color: string; bg: string; dot: string }> = {
  calm:     { label: 'Calm',     color: 'text-teal-700',   bg: 'bg-teal-50',    dot: 'bg-teal-400' },
  stressed: { label: 'Stressed', color: 'text-orange-700', bg: 'bg-orange-50',  dot: 'bg-orange-400' },
  anxious:  { label: 'Anxious',  color: 'text-amber-700',  bg: 'bg-amber-50',   dot: 'bg-amber-400' },
  happy:    { label: 'Happy',    color: 'text-green-700',  bg: 'bg-green-50',   dot: 'bg-green-400' },
  sad:      { label: 'Sad',      color: 'text-blue-700',   bg: 'bg-blue-50',    dot: 'bg-blue-400' },
  angry:    { label: 'Angry',    color: 'text-red-700',    bg: 'bg-red-50',     dot: 'bg-red-400' },
  neutral:  { label: 'Neutral',  color: 'text-slate-600',  bg: 'bg-slate-100',  dot: 'bg-slate-400' },
}