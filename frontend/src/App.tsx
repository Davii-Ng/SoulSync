import { Header } from "./components/Header"
import { EmotionBadge } from "./components/EmotionBadge"
import { VoiceOrb } from "./components/VoiceOrb"
import type { OrbState, Message, Emotion } from "./types"
import { useState, useEffect } from "react"
import { ChatTranscript } from "./components/ChatTranscript"
import { useWebSocket } from './hooks/useWebSocket'
import { useVoiceInput } from './hooks/useVoiceInput'

function App() {
  const [orbState, setOrbState] = useState<OrbState>('idle')
  const [messages, setMessages] = useState<Message[]>([])
  const [emotion, setEmotion] = useState<Emotion>('neutral')
  const { isConnected, sendMessage, ws } = useWebSocket()
  const { isListening, transcript, startListening, stopListening } = useVoiceInput()

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
        }
        setMessages((prev) => [...prev, aiMsg])
      }

      if (data.emotion) {
        setEmotion(data.emotion)
      }

      setOrbState('idle')
    }
  }, [ws.current])

  const handleOrbClick = () => {
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
        }
        setMessages((prev) => [...prev, userMsg])
        sendMessage(text)
        setOrbState('thinking')
      } else {
        setOrbState('idle')
      }
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <Header />
      <EmotionBadge emotion={emotion} />
      <VoiceOrb state={orbState} onClick={handleOrbClick} />
      <ChatTranscript messages={messages} />
    </div>
  )
}

export default App