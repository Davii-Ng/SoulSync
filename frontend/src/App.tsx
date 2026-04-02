import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { SpeakingPage } from './pages/speaking'
import { JournalPage } from './pages/JournalPage'
import { CalendarPage } from './pages/CalendarPage'
import { HistoryPage } from './pages/HistoryPage'
import { ResourcesPage } from './pages/ResourcesPage'
import { SettingsPage } from './pages/SettingsPage'
import { useWebSocket } from './hooks/useWebSocket'
import { useVoiceInput } from './hooks/useVoiceInput'
import type { OrbState, Message, Emotion, SavedEvent, WsResponse, JournalEntry } from './types'
import { useState, useEffect, useCallback, useRef } from 'react'

const getEventId = (event: SavedEvent): string => {
  const trimmed = event.id?.trim()
  if (trimmed) return trimmed
  return `${event.title}|${event.dateLabel}`.toLowerCase()
}

const mergeEvents = (existing: SavedEvent[], incoming: SavedEvent[]): SavedEvent[] => {
  if (incoming.length === 0) return existing
  const byId = new Map<string, SavedEvent>()
  for (const event of existing) {
    byId.set(getEventId(event), { ...event, id: getEventId(event) })
  }
  for (const event of incoming) {
    const normalized = { ...event, id: getEventId(event) }
    byId.set(normalized.id, normalized)
  }
  return Array.from(byId.values())
}

// Phrases that signal the user wants to save today's journal
const SAVE_PHRASES = [
  'save today', 'save journal', 'save this conversation', 'save my journal',
  "that's it for today", 'thats it for today', 'done for the day', 'done for today',
  'wrap up', 'end session', 'save the chat', 'save chat',
]

function isSaveIntent(text: string): boolean {
  const lower = text.toLowerCase()
  return SAVE_PHRASES.some((p) => lower.includes(p))
}

function App() {
  const [orbState, setOrbState] = useState<OrbState>('idle')
  const [messages, setMessages] = useState<Message[]>([])
  const [emotion, setEmotion] = useState<Emotion>('neutral')
  const [savedEvents, setSavedEvents] = useState<SavedEvent[]>([])
  const [savedJournals, setSavedJournals] = useState<JournalEntry[]>(() => {
    try {
      const stored = localStorage.getItem('soulsync_journals')
      return stored ? JSON.parse(stored) : []
    } catch { return [] }
  })
  const [selectedVoiceId, setSelectedVoiceId] = useState<string | null>(
    () => localStorage.getItem('soulsync_voice_id'),
  )
  const [selectedVoiceName, setSelectedVoiceName] = useState<string | null>(
    () => localStorage.getItem('soulsync_voice_name'),
  )
  // Snapshot current conversation as a daily journal entry (instant, no backend needed)
  const snapshotJournal = useCallback(() => {
    const today = new Date().toISOString().slice(0, 10)
    setMessages((prev) => {
      if (prev.length === 0) return prev
      const stripped = prev.map(({ audio_base64: _, ...rest }) => rest)
      setSavedJournals((journals) => {
        const idx = journals.findIndex((j) => j.date === today)
        const entry: JournalEntry = { id: today, date: today, messages: stripped, savedAt: Date.now() }
        if (idx >= 0) {
          const updated = [...journals]
          updated[idx] = entry
          return updated
        }
        return [entry, ...journals]
      })
      return prev
    })
  }, [])

  const { isConnected, sendMessage, setVoice, ws } = useWebSocket()
  const { isListening, transcript, startListening, stopListening } = useVoiceInput()
  const listeningRef = useRef(false)

  useEffect(() => {
    listeningRef.current = isListening
  }, [isListening])

  useEffect(() => {
    const socket = ws.current
    if (!socket) return

    const handleMessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data) as WsResponse

      if (data.type === 'error') {
        const errMsg: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: data.content || 'Something went wrong.',
          timestamp: Date.now(),
        }
        setMessages((prev) => [...prev, errMsg])
        setOrbState('idle')
        return
      }

      if (data.content) {
        const aiMsg: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: data.content,
          timestamp: Date.now(),
          emotion: data.emotion,
          audio_base64: data.audio_base64,
        }
        setMessages((prev) => [...prev, aiMsg])
      }

      if (data.emotion) {
        setEmotion(data.emotion)
      }

      if (data.events && data.events.length > 0) {
        setSavedEvents((prev) => mergeEvents(prev, data.events ?? []))
      }

      // Backend fallback: re-snapshot if agent also flagged journal_saved
      if (data.journal_saved) snapshotJournal()

      if (data.tts_error) {
        const note: Message = {
          id: (Date.now() + 2).toString(),
          role: 'assistant',
          content: data.tts_error,
          timestamp: Date.now(),
        }
        setMessages((prev) => [...prev, note])
      }

      if (data.audio_base64) {
        setOrbState('speaking')
        const audio = new Audio(`data:audio/mpeg;base64,${data.audio_base64}`)
        audio.onended = () => setOrbState('idle')
        audio.play().catch(() => setOrbState('idle'))
      } else {
        setOrbState('idle')
      }
    }

    socket.addEventListener('message', handleMessage)
    return () => socket.removeEventListener('message', handleMessage)
  }, [isConnected, ws])

  const handleTextSend = useCallback(
    (text: string) => {
      // Save journal instantly on save-intent — no backend round-trip needed
      if (isSaveIntent(text)) snapshotJournal()

      const userMsg: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: text,
        timestamp: Date.now(),
        isVoice: false,
      }
      setMessages((prev) => [...prev, userMsg])
      const sent = sendMessage(text)
      if (sent) {
        setOrbState('thinking')
      } else {
        const errMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Not connected to server. Please check that the backend is running.',
          timestamp: Date.now(),
        }
        setMessages((prev) => [...prev, errMsg])
      }
    },
    [sendMessage, snapshotJournal],
  )

  const handleOrbClick = useCallback(async () => {
    if (listeningRef.current) {
      const text = await stopListening()
      if (!text) {
        setOrbState('idle')
      }
    } else if (orbState === 'listening') {
      setOrbState('idle')
    } else if (orbState === 'idle') {
      startListening((text: string) => {
        if (isSaveIntent(text)) snapshotJournal()

        const userMsg: Message = {
          id: Date.now().toString(),
          role: 'user',
          content: text,
          timestamp: Date.now(),
          isVoice: true,
        }
        setMessages((prev) => [...prev, userMsg])
        const sent = sendMessage(text)
        if (sent) {
          setOrbState('thinking')
        } else {
          const errMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: 'Not connected to server. Please check that the backend is running.',
            timestamp: Date.now(),
          }
          setMessages((prev) => [...prev, errMsg])
          setOrbState('idle')
        }
      })
      setOrbState('listening')
    }
  }, [orbState, startListening, stopListening, sendMessage, snapshotJournal])

  const handleVoiceChange = useCallback(
    (voiceId: string | null, voiceName: string | null) => {
      setSelectedVoiceId(voiceId)
      setSelectedVoiceName(voiceName)
      if (voiceId) localStorage.setItem('soulsync_voice_id', voiceId)
      else localStorage.removeItem('soulsync_voice_id')
      if (voiceName) localStorage.setItem('soulsync_voice_name', voiceName)
      else localStorage.removeItem('soulsync_voice_name')
      setVoice(voiceId)
    },
    [setVoice],
  )

  // Persist journals to localStorage
  useEffect(() => {
    localStorage.setItem('soulsync_journals', JSON.stringify(savedJournals))
  }, [savedJournals])

  // Send stored voice preference when WebSocket connects
  useEffect(() => {
    if (isConnected && selectedVoiceId) {
      setVoice(selectedVoiceId)
    }
  }, [isConnected, selectedVoiceId, setVoice])

  const isBusy = orbState === 'thinking' || orbState === 'speaking'

  return (
    <Routes>
      <Route element={<Layout isConnected={isConnected} />}>
        <Route
          index
          element={
            <SpeakingPage
              orbState={orbState}
              messages={messages}
              emotion={emotion}
              transcript={transcript}
              isBusy={isBusy}
              savedEvents={savedEvents}
              voiceName={selectedVoiceName}
              onOrbClick={handleOrbClick}
              onTextSend={handleTextSend}
            />
          }
        />
        <Route path="journal" element={<JournalPage journals={savedJournals} />} />
        <Route path="calendar" element={<CalendarPage events={savedEvents} />} />
        <Route path="history" element={<HistoryPage messages={messages} />} />
        <Route path="resources" element={<ResourcesPage />} />
        <Route path="settings" element={<SettingsPage selectedVoiceId={selectedVoiceId} onVoiceChange={handleVoiceChange} />} />
      </Route>
    </Routes>
  )
}

export default App
