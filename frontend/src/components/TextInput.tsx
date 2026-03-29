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
        className="soul-input-wrap flex-1 flex items-center rounded-full px-4"
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
          className="flex-1 py-3 text-sm bg-transparent outline-none placeholder:text-[var(--soul-text-muted)]"
          style={{ color: 'var(--soul-text)' }}
        />
      </div>

      {/* Send / Thinking button */}
      <button
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        className="h-9 rounded-full flex items-center justify-center gap-1.5 transition-all hover:scale-105 active:scale-95 disabled:hover:scale-100"
        style={{
          background: disabled
            ? 'var(--soul-accent-light)'
            : text.trim()
              ? 'var(--soul-accent)'
              : 'var(--soul-border-light)',
          paddingInline: disabled ? '12px' : '0',
          width: disabled ? 'auto' : '36px',
          opacity: disabled ? 0.8 : !text.trim() ? 0.3 : 1,
        }}
      >
        {disabled ? (
          <>
            <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="white" strokeWidth="2.5" strokeLinecap="round">
              <path d="M12 2a10 10 0 0 1 10 10" />
            </svg>
            <span className="text-xs font-medium text-white">Thinking...</span>
          </>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22,2 15,22 11,13 2,9"/>
          </svg>
        )}
      </button>
    </div>
  )
}