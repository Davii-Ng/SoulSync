import { useState, useCallback } from 'react'

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

  return (
    <div className="flex items-center" style={{ gap: '15px' }}>
      <div
        className="flex-1 flex items-center pl-8 pr-5 rounded-full"
        style={{
          background: 'var(--soul-surface-alt)',
          border: '1px solid var(--soul-border)',
          height: '48px',
        }}
      >
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              handleSend()
            }
          }}
          placeholder="Type a message..."
          disabled={disabled}
          className="flex-1 text-sm bg-transparent outline-none"
          style={{ color: 'var(--soul-text)' }}
        />
      </div>

      <button
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        className="h-11 w-11 flex-shrink-0 rounded-full flex items-center justify-center transition-all hover:scale-105 active:scale-95"
        style={{
          background: text.trim() ? 'var(--soul-accent)' : 'var(--soul-border)',
          opacity: disabled ? 0.6 : !text.trim() ? 0.4 : 1,
        }}
      >
        {disabled ? (
          <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <path d="M12 2a10 10 0 0 1 10 10" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22,2 15,22 11,13 2,9"/>
          </svg>
        )}
      </button>
    </div>
  )
}
