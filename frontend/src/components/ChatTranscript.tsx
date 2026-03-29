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
    <div className="min-h-[240px] max-h-[420px] overflow-y-auto space-y-3 pr-1 flex flex-col">
      {messages.length === 0 ? (
        <div className="flex-1 flex items-center justify-center min-h-[200px]">
          <p className="text-center text-sm" style={{ color: 'var(--soul-text-muted)' }}>
            Start speaking to begin a conversation
          </p>
        </div>
      ) : (
        messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
      )}
      <div ref={bottomRef} />
    </div>
  )
}
