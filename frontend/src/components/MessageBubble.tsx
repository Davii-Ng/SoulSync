// Chat bubble styled as left/right outlined capsules

import type { Message } from '../types'

interface Props {
  message: Message
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex msg-enter ${isUser ? 'justify-start' : 'justify-end'}`}>
      <div
        className="max-w-[85%] px-4 py-3 rounded-2xl text-lg leading-relaxed border"
        style={{
          borderColor: 'var(--soul-border)',
          background: 'rgba(255, 255, 255, 0.02)',
          color: 'var(--soul-text)',
        }}
      >
        <span style={{ color: 'var(--soul-text-secondary)' }}>
          {isUser ? 'User: ' : 'AI: '}
        </span>
        {message.content}
      </div>
    </div>
  )
}