import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { SpeakingPage } from './pages/SpeakingPage'
import { JournalPage } from './pages/JournalPage'
import { CalendarPage } from './pages/CalendarPage'
import { HistoryPage } from './pages/HistoryPage'
import { ResourcesPage } from './pages/ResourcesPage'
import { SettingsPage } from './pages/SettingsPage'
import { useWebSocket } from './hooks/useWebSocket'
import { useVoiceInput } from './hooks/useVoiceInput'
import type { OrbState, Message, Emotion, SavedEvent } from './types'
import { useState, useEffect, useCallback, useRef } from 'react'

function App() {
  const [orbState, setOrbState] = useState<OrbState>('idle')
  const [messages, setMessages] = useState<Message[]>([])
  const [emotion, setEmotion] = useState<Emotion>('neutral')
  const [savedEvents] = useState<SavedEvent[]>([
    {
      id: '1',
      title: 'Therapy check-in reminder',
      dateLabel: 'Monday, 7:30 PM',
      note: 'Captured from your latest conversation.',
    },
  ])
  const { isConnected, sendMessage, ws } = useWebSocket()
  const { isListening, transcript, startListening, stopListening } = useVoiceInput()
  const listeningRef = useRef(false)

  useEffect(() => {
    listeningRef.current = isListening
  }, [isListening])

  useEffect(() => {
    const socket = ws.current
    if (!socket) return

    const handleMessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data)

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
    [sendMessage],
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
  }, [orbState, startListening, stopListening, sendMessage])

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
              onOrbClick={handleOrbClick}
              onTextSend={handleTextSend}
            />
          }
        />
        <Route path="journal" element={<JournalPage messages={messages} />} />
        <Route path="calendar" element={<CalendarPage events={savedEvents} />} />
        <Route path="history" element={<HistoryPage messages={messages} />} />
        <Route path="resources" element={<ResourcesPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default App
