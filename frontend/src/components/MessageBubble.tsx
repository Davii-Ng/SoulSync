// Chat bubble styled by role - AI left with avatar, user right

import type { Message } from '../types'
import { AudioPlayer } from './AudioPlayer'

interface Props {
  message: Message
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end msg-enter">
        <div className="max-w-[75%]">
          {/* Voice indicator */}
          {message.isVoice && (
            <div className="flex items-center gap-1 justify-end mb-1">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none"
                stroke="var(--soul-user-text)" strokeWidth="2.5" strokeLinecap="round">
                <path d="M12 3a4 4 0 0 1 4 4v4a4 4 0 0 1-8 0V7a4 4 0 0 1 4-4z"/>
              </svg>
              <span className="text-[10px] font-medium" style={{ color: 'var(--soul-user-text)' }}>
                Voice
              </span>
            </div>
          )}
          <div
            className="px-3.5 py-2.5 rounded-2xl rounded-br-sm text-sm leading-relaxed"
            style={{ background: 'var(--soul-user-bubble)', color: 'var(--soul-user-text)' }}
          >
            {message.content}
          </div>
        </div>
      </div>
    )
  }

  // AI message
  return (
    <div className="flex gap-2 items-start msg-enter">
      {/* AI avatar */}
      <div
        className="w-7 h-7 rounded-full flex-shrink-0 mt-0.5"
        style={{ background: 'linear-gradient(135deg, var(--soul-gradient-start), var(--soul-gradient-end))' }}
      />
      <div className="max-w-[75%]">
        <div
          className="px-3.5 py-2.5 rounded-2xl rounded-bl-sm text-sm leading-relaxed"
          style={{
            background: 'var(--soul-surface)',
            border: '1px solid var(--soul-border-light)',
            color: 'var(--soul-text)',
          }}
        >
          {message.content}
          {/* Inline audio player */}
          {message.audio_base64 && (
            <AudioPlayer audio_base64={message.audio_base64} />
          )}
        </div>
      </div>
    </div>
  )
}