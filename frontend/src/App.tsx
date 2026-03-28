import { Header } from "./components/Header"
import { EmotionBadge } from "./components/EmotionBadge"
import { VoiceOrb } from "./components/VoiceOrb"
import type { OrbState, Message, Emotion } from "./types"
import { useState } from "react"
import { ChatTranscript } from "./components/ChatTranscript"

function App() {
  const [orbState, setOrbState] = useState<OrbState>('idle')
  const [messages, setMessages] = useState<Message[]>([])
  const [emotion, setEmotion] = useState<Emotion>('neutral')

  const handleOrbClick = () => {
    setOrbState(orbState === 'idle' ? 'listening' : 'idle')
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