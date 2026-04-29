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
    <div className="flex items-center gap-4">
      <div className="flex-1 flex items-center pl-8 pr-5 rounded-full h-12 bg-soul-surface-alt border border-soul-border">
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
          className="flex-1 text-sm bg-transparent outline-none text-soul-text"
        />
      </div>

      <button
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        className={`h-11 w-11 flex-shrink-0 rounded-full flex items-center justify-center transition-all hover:scale-105 active:scale-95 ${
          text.trim() ? 'bg-soul-accent' : 'bg-soul-border'
        } ${disabled ? 'opacity-60' : !text.trim() ? 'opacity-40' : ''}`}
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
