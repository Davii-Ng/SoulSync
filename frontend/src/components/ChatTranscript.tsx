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
      <h2 className="tech-font text-[var(--soul-accent-light)] mb-3">
        &gt; CHAT_LOG
      </h2>
      <div className="min-h-[380px] max-h-[500px] md:max-h-[640px] overflow-y-auto space-y-3 pr-2 flex flex-col">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center min-h-[300px]">
            <p className="text-center text-base" style={{ color: 'var(--soul-text-muted)' }}>
              Start speaking to begin a conversation
            </p>
          </div>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}