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
      <h2 className="text-4xl font-semibold mb-4" style={{ color: 'var(--soul-text)' }}>
        Chat transcript
      </h2>
      <div className="min-h-[160px] max-h-[280px] md:max-h-[340px] overflow-y-auto space-y-4 pr-1">
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