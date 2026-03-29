import { Header } from './components/Header'
import { VoiceOrb } from './components/VoiceOrb'
import { ChatTranscript } from './components/ChatTranscript'
import { TextInput } from './components/TextInput'
import { useWebSocket } from './hooks/useWebSocket'
import { useVoiceInput } from './hooks/useVoiceInput'
import { EmotionBadge } from './components/EmotionBadge'
import type { OrbState, Message, Emotion, SavedEvent } from './types'
import { useState, useEffect, useCallback } from 'react'

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
  const { startListening, stopListening } = useVoiceInput()

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!ws.current) return

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)

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

      // Play audio automatically if available
      if (data.audio_base64) {
        setOrbState('speaking')
        const audio = new Audio(`data:audio/mpeg;base64,${data.audio_base64}`)
        audio.onended = () => setOrbState('idle')
        audio.play().catch(() => setOrbState('idle'))
      } else {
        setOrbState('idle')
      }
    }

    return () => {
      if (ws.current) {
        ws.current.onmessage = null
      }
    }
  }, [isConnected, ws])

  // Send text message (from TextInput)
  const handleTextSend = useCallback((text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: Date.now(),
      isVoice: false,
    }
    setMessages((prev) => [...prev, userMsg])
    sendMessage(text)
    setOrbState('thinking')
  }, [sendMessage])

  // Handle orb click (voice input)
  // handleOrbClick — thêm async và await
  const handleOrbClick = useCallback(async () => {
    if (orbState === 'idle') {
      startListening()
      setOrbState('listening')
    } else if (orbState === 'listening') {
      const text = await stopListening()  // ← thêm await
      if (text) {
        const userMsg: Message = {
          id: Date.now().toString(),
          role: 'user',
          content: text,
          timestamp: Date.now(),
          isVoice: true,
        }
        setMessages((prev) => [...prev, userMsg])
        sendMessage(text)
        setOrbState('thinking')
      } else {
        setOrbState('idle')
      }
    }
  }, [orbState, startListening, stopListening, sendMessage])

  const isBusy = orbState === 'thinking' || orbState === 'speaking'

  return (
    <div
      className="min-h-screen soul-dashboard px-4 py-5 md:px-8 md:py-8"
      style={{ background: 'var(--soul-bg)' }}
    >
      <div className="w-full flex flex-col gap-4 md:gap-6">
        <Header isConnected={isConnected} />

        <section
          className="dashboard-strip rounded-xl border px-5 py-3 flex items-center justify-center gap-3"
          style={{ borderColor: 'var(--soul-border-light)' }}
        >
          <span className="text-sm" style={{ color: 'var(--soul-text-secondary)' }}>
            Emotion signal:
          </span>
          <EmotionBadge emotion={emotion} />
          <span className="text-sm" style={{ color: 'var(--soul-text-muted)' }}>
            tone adapts with mood in real time
          </span>
        </section>

        <section className="flex flex-col items-center py-3 md:py-4">
          <VoiceOrb state={orbState} onClick={handleOrbClick} />
          <p className="text-sm mt-2" style={{ color: 'var(--soul-text-muted)' }}>
            idle / listening / thinking / speaking
          </p>
        </section>

        <section
          className="dashboard-chat rounded-xl border p-4 md:p-5"
          style={{ borderColor: 'var(--soul-border-light)' }}
        >
          <ChatTranscript messages={messages} />
          <div className="mt-5">
            <TextInput onSend={handleTextSend} disabled={isBusy} />
          </div>
        </section>

        <section className="pt-1 md:pt-0">
          <p className="text-base text-center mb-3" style={{ color: 'var(--soul-text-secondary)' }}>
            Phase 2 cards
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
            <article className="dashboard-card rounded-xl border p-5" style={{ borderColor: 'var(--soul-border-light)' }}>
              <h3 className="text-lg font-semibold" style={{ color: 'var(--soul-text)' }}>Mood History</h3>
              <p className="text-sm mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                Mini trend chart and sentiment trajectory.
              </p>
            </article>

            <article className="dashboard-card rounded-xl border p-5" style={{ borderColor: 'var(--soul-border-light)' }}>
              <h3 className="text-lg font-semibold" style={{ color: 'var(--soul-text)' }}>Events</h3>
              <p className="text-sm mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                {savedEvents[0]?.title ?? 'Captured by calendar agent'}
              </p>
            </article>

            <article className="dashboard-card rounded-xl border p-5" style={{ borderColor: 'var(--soul-border-light)' }}>
              <h3 className="text-lg font-semibold" style={{ color: 'var(--soul-text)' }}>Resources</h3>
              <p className="text-sm mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                Hotlines, grounding prompts, and mindfulness links.
              </p>
            </article>
          </div>
        </section>
      </div>
    </div>
  )
}

export default App