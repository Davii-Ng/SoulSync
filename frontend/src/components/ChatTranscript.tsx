// Scrollable list of user/AI message bubbles

import type { Message } from '../types'
import { MessageBubble } from './MessageBubble'

interface Props {
  messages: Message[]
}

export function ChatTranscript({ messages }: Props) {
  return (
    <div className="dashboard-transcript p-2 md:p-3">
      <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--soul-text)' }}>
        Chat transcript
      </h2>
      <div className="max-h-[280px] md:max-h-[360px] overflow-y-auto space-y-4 pr-1">
        {messages.length === 0 ? (
          <p className="text-center text-sm py-8" style={{ color: 'var(--soul-text-muted)' }}>
            Start speaking to begin a conversation
          </p>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
      </div>
    </div>
  )
}