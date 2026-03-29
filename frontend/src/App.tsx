import { Header } from './components/Header'
import { VoiceOrb } from './components/VoiceOrb'
import { ChatTranscript } from './components/ChatTranscript'
import { TextInput } from './components/TextInput'
import { useWebSocket } from './hooks/useWebSocket'
import { useVoiceInput } from './hooks/useVoiceInput'
import type { OrbState, Message, Emotion } from './types'
import { useState, useEffect, useCallback } from 'react'

function App() {
  const [orbState, setOrbState] = useState<OrbState>('idle')
  const [messages, setMessages] = useState<Message[]>([])
  const [emotion, setEmotion] = useState<Emotion>('neutral')
  const { isConnected, sendMessage, ws } = useWebSocket()
  const { transcript, startListening, stopListening } = useVoiceInput()

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
  }, [ws.current])

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
  const handleOrbClick = useCallback(() => {
    if (orbState === 'idle') {
      startListening()
      setOrbState('listening')
    } else if (orbState === 'listening') {
      const text = stopListening()
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
      className="h-screen flex flex-col"
      style={{ background: 'var(--soul-bg)' }}
    >
      {/* Header with emotion badge */}
      <Header emotion={emotion} isConnected={isConnected} />

      {/* Chat area (takes all available space) */}
      <ChatTranscript messages={messages} />

      {/* Bottom: orb + text input */}
      <div
        className="px-4 pt-3 pb-4 border-t"
        style={{ borderColor: 'var(--soul-border-light)', background: 'var(--soul-surface)' }}
      >
        {/* Voice orb centered */}
        <div className="flex justify-center mb-3">
          <VoiceOrb state={orbState} onClick={handleOrbClick} />
        </div>

        {/* Text input */}
        <TextInput onSend={handleTextSend} disabled={isBusy} />
      </div>
    </div>
  )
}

export default App