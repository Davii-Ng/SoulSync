// Text input with send button for typing messages

import { useState, useCallback, type KeyboardEvent } from 'react'

interface Props {
  onSend: (text: string) => void
  disabled?: boolean
}

export function TextInput({ onSend, disabled = false }: Props) {
  const [text, setText] = useState('')

  const handleSend = useCallback(() => {
    const trimmed = text.trim()
    if (trimmed && !disabled) {
      onSend(trimmed)
      setText('')
    }
  }, [text, disabled, onSend])

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  return (
    <div className="flex items-center gap-2">
      <div
        className="flex-1 flex items-center rounded-full px-4 transition-colors"
        style={{
          background: 'var(--soul-surface)',
          border: '1px solid var(--soul-border-light)',
        }}
      >
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={disabled}
          className="flex-1 py-2.5 text-sm bg-transparent outline-none placeholder:text-[var(--soul-text-muted)]"
          style={{ color: 'var(--soul-text)' }}
        />
      </div>

      {/* Send button */}
      <button
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        className="w-9 h-9 rounded-full flex items-center justify-center transition-all hover:scale-105 active:scale-95 disabled:opacity-30 disabled:hover:scale-100"
        style={{
          background: text.trim()
            ? 'linear-gradient(135deg, var(--soul-gradient-start), var(--soul-gradient-end))'
            : 'var(--soul-border-light)',
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
          stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22,2 15,22 11,13 2,9"/>
        </svg>
      </button>
    </div>
  )
}