// Scrollable list of user/AI message bubbles

import type { Message } from '../types'
import { MessageBubble } from './MessageBubble'

interface Props {
  messages: Message[]
}

export function ChatTranscript({ messages }: Props) {
  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
      {messages.length === 0 ? (
        <p className="text-center text-gray-500 text-sm">
          Start speaking to begin a conversation
        </p>
      ) : (
        messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
      )}
    </div>
  )
}