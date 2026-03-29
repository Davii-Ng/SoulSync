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

      // Backend error — show as system message, reset orb
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

  // Called when browser speech recognition produces a final transcript
  const handleVoiceResult = useCallback((text: string) => {
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
  }, [sendMessage])

  // Handle orb click (voice input)
  const handleOrbClick = useCallback(() => {
    if (orbState === 'idle') {
      startListening(handleVoiceResult)
      setOrbState('listening')
    } else if (orbState === 'listening') {
      stopListening()
      // Result arrives async via handleVoiceResult callback when recognition ends
      // If no speech was detected, onend fires without calling the callback → orb stays idle
      setOrbState('idle')
    }
  }, [orbState, startListening, stopListening, handleVoiceResult])

  const isBusy = orbState === 'thinking' || orbState === 'speaking'

  return (
    <div
      className="min-h-screen soul-dashboard px-4 py-5 md:px-8 md:py-8"
      style={{ background: 'var(--soul-bg)' }}
    >
      <div className="w-full max-w-5xl mx-auto flex flex-col gap-4 md:gap-6">
        <Header isConnected={isConnected} />

        <section
          className="dashboard-strip rounded-2xl border px-5 py-3.5 flex items-center justify-center gap-4"
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

        <section className="flex flex-col items-center py-4 md:py-6">
          <VoiceOrb state={orbState} onClick={handleOrbClick} />
        </section>

        <section
          className="dashboard-chat rounded-2xl border p-4 md:p-5"
          style={{ borderColor: 'var(--soul-border-light)' }}
        >
          <ChatTranscript messages={messages} />
          <div className="mt-5">
            <TextInput onSend={handleTextSend} disabled={isBusy} />
          </div>
        </section>

        <section className="pt-1 md:pt-0">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
            {/* Mood History — static emotion timeline */}
            <article className="dashboard-card dashboard-card-hover rounded-2xl border p-5" style={{ borderColor: 'var(--soul-border-light)' }}>
              <h3 className="text-lg section-heading" style={{ color: 'var(--soul-text)' }}>Mood History</h3>
              <div className="flex items-center gap-3 mt-4">
                {[
                  { day: 'Mon', dot: 'bg-green-400' },
                  { day: 'Tue', dot: 'bg-teal-400' },
                  { day: 'Wed', dot: 'bg-amber-400' },
                  { day: 'Thu', dot: 'bg-blue-400' },
                  { day: 'Fri', dot: 'bg-orange-400' },
                  { day: 'Today', dot: 'bg-green-400' },
                ].map((item) => (
                  <div key={item.day} className="flex flex-col items-center gap-1.5">
                    <span className={`w-3 h-3 rounded-full ${item.dot}`} />
                    <span className="text-xs" style={{ color: 'var(--soul-text-muted)' }}>{item.day}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs mt-3" style={{ color: 'var(--soul-text-muted)' }}>
                Mostly positive this week
              </p>
            </article>

            {/* Events — show saved event */}
            <article className="dashboard-card dashboard-card-hover rounded-2xl border p-5" style={{ borderColor: 'var(--soul-border-light)' }}>
              <h3 className="text-lg section-heading" style={{ color: 'var(--soul-text)' }}>Events</h3>
              <div
                className="mt-3 rounded-lg px-3.5 py-2.5"
                style={{ background: 'var(--soul-accent-pale)', border: '1px solid var(--soul-accent-light)' }}
              >
                <p className="text-sm font-medium" style={{ color: 'var(--soul-text)' }}>
                  {savedEvents[0]?.title}
                </p>
                <p className="text-xs mt-1" style={{ color: 'var(--soul-accent)' }}>
                  {savedEvents[0]?.dateLabel}
                </p>
              </div>
              <p className="text-xs mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                {savedEvents[0]?.note}
              </p>
            </article>

            {/* Resources — static helpful links */}
            <article className="dashboard-card dashboard-card-hover rounded-2xl border p-5" style={{ borderColor: 'var(--soul-border-light)' }}>
              <h3 className="text-lg section-heading mb-3" style={{ color: 'var(--soul-text)' }}>Resources</h3>
              {[
                { icon: '\u260E', label: '988 Suicide & Crisis Lifeline', sub: 'Call or text 988' },
                { icon: '\uD83C\uDF2C\uFE0F', label: 'Box Breathing', sub: 'Inhale 4s, hold 4s, exhale 4s' },
                { icon: '\uD83E\uDDD8', label: '5-4-3-2-1 Grounding', sub: 'Name 5 things you can see...' },
              ].map((r) => (
                <div
                  key={r.label}
                  className="flex items-start gap-2.5 py-1.5 cursor-pointer resource-row rounded-md px-1 -mx-1"
                >
                  <span className="text-sm mt-0.5">{r.icon}</span>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--soul-text)' }}>{r.label}</p>
                    <p className="text-xs" style={{ color: 'var(--soul-text-muted)' }}>{r.sub}</p>
                  </div>
                </div>
              ))}
            </article>
          </div>
        </section>
      </div>
    </div>
  )
}

export default App