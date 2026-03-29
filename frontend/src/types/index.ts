// Type definitions for SoulSync: emotions, orb states, and chat messages

export type Emotion = 'calm' | 'stressed' | 'anxious' | 'happy' | 'sad' | 'angry' | 'neutral' | 'crisis'

export type OrbState = 'idle' | 'listening' | 'thinking' | 'speaking'

export type AppTab = 'speak' | 'journal' | 'calendar' | 'history' | 'resources'

export interface SavedEvent {
  id: string
  title: string
  dateLabel: string
  note?: string
}

export interface Voice {
  voice_id: string
  name: string
}

export interface WsResponse {
  type?: 'response' | 'error' | 'transcript' | 'voice_set'
  content?: string
  emotion?: Emotion
  audio_base64?: string
  tts_error?: string
  events?: SavedEvent[]
  voice_id?: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  emotion?: Emotion
  audio_base64?: string
  isVoice?: boolean
}