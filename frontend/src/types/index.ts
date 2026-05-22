// Type definitions for SoulSync: emotions, orb states, and chat messages

export type Emotion = 'calm' | 'stressed' | 'anxious' | 'happy' | 'sad' | 'angry' | 'neutral' | 'crisis'

export type OrbState = 'idle' | 'listening' | 'thinking' | 'speaking'

export type AppTab = 'speak' | 'journal' | 'calendar' | 'home' | 'resources'

export interface SavedEvent {
  id: string
  title: string
  dateLabel: string
  note?: string
}

export interface Voice {
  voice_id: string
  name: string
  gender: 'male' | 'female' | 'unknown'
}

export interface WsResponse {
  type?: 'response' | 'text_ready' | 'audio_ready' | 'audio_error' | 'error' | 'transcript' | 'voice_set'
  content?: string
  emotion?: Emotion
  audio_base64?: string
  tts_error?: string
  events?: SavedEvent[]
  voice_id?: string
  journal_saved?: boolean
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

export interface JournalEntry {
  id: string
  date: string          // "YYYY-MM-DD"
  messages: Message[]   // conversation snapshot (audio stripped)
  savedAt: number
}