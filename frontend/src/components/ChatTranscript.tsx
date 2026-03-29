// Scrollable list of user/AI message bubbles

import type { Message } from '../types'
import { MessageBubble } from './MessageBubble'
import { useEffect, useRef } from 'react'

interface Props {
  messages: Message[]
}

export function ChatTranscript({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (  
    <div className="dashboard-transcript p-2 md:p-3">
      <h2 className="text-xl section-heading mb-3" style={{ color: 'var(--soul-text)' }}>
        Conversation
      </h2>
      <div className="min-h-[200px] max-h-[320px] md:max-h-[380px] overflow-y-auto space-y-3 pr-1">
        {messages.length === 0 ? (
          <p className="text-center text-base py-8" style={{ color: 'var(--soul-text-muted)' }}>
            Start speaking to begin a conversation
          </p>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}