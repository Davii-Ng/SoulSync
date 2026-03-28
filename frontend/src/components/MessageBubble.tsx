// Single chat bubble, styled by role (user/assistant)

import type { Message } from '../types'

interface Props {
  message: Message
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-start' : 'justify-end'}`}>
      <div
        className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm ${
          isUser
            ? 'bg-white/10 text-gray-200'
            : 'bg-purple-500/20 text-purple-100'
        }`}
      >
        {message.content}
      </div>
    </div>
  )
}