import { Header } from "./components/Header"
import { EmotionBadge } from "./components/EmotionBadge"
import { VoiceOrb } from "./components/VoiceOrb"
import type { OrbState, Message } from "./types"
import { useState } from "react"
import { ChatTranscript } from "./components/ChatTranscript"

const dummyMessages: Message[] = [
  { id: '1', role: 'user', content: 'I feel so tired lately...', timestamp: Date.now() },
  { id: '2', role: 'assistant', content: 'I hear you. It sounds like you\'ve been carrying a lot. Want to tell me more about what\'s been going on?', timestamp: Date.now() },
  { id: '3', role: 'user', content: 'Work has been really crazy this week.', timestamp: Date.now() },
  { id: '4', role: 'assistant', content: 'That sounds really tough. Taking a moment to talk about it is a good step.', timestamp: Date.now() },
]

function App() {
  const [orbState, setOrbState] = useState<OrbState>('idle')

  const handleOrbClick = () => {
    setOrbState(orbState === 'idle' ? 'listening' : 'idle')
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <Header />
      <EmotionBadge emotion="calm" />
      <VoiceOrb state={orbState} onClick={handleOrbClick} />
      <ChatTranscript messages={dummyMessages} />
    </div>
  )
}

export default App