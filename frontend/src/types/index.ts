export type Emotion = 'calm' | 'stressed' | 'anxious' | 'happy' | 'sad' | 'angry' | 'neutral'

export type OrbState = 'idle' | 'listening' | 'thinking' | 'speaking'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  emotion?: Emotion
}