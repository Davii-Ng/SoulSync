// Chat bubble with distinct user/AI styling

import type { Message } from '../types'

interface Props {
  message: Message
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex msg-enter ${isUser ? 'justify-start' : 'justify-end'}`}>
      <div
        className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser ? 'bubble-user' : 'bubble-ai'
        }`}
      >
        <span
          className="text-xs font-medium block mb-1"
          style={{ color: 'var(--soul-text-muted)' }}
        >
          {isUser ? 'You' : 'SoulSync'}
        </span>
        <span style={{ color: 'var(--soul-text)' }}>{message.content}</span>
      </div>
    </div>
  )
}
