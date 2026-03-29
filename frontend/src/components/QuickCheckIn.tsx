import { useState, useCallback } from 'react'

interface Props {
  onCheckIn: (mood: string, label: string) => void
}

const MOODS = [
  { emoji: '\uD83E\uDD29', label: 'Amazing', value: 'happy' },
  { emoji: '\uD83D\uDE0C', label: 'Peaceful', value: 'calm' },
  { emoji: '\uD83E\uDD14', label: 'Unsure', value: 'neutral' },
  { emoji: '\uD83D\uDE1F', label: 'Worried', value: 'anxious' },
  { emoji: '\uD83D\uDE22', label: 'Sad', value: 'sad' },
  { emoji: '\uD83D\uDE24', label: 'Frustrated', value: 'angry' },
  { emoji: '\uD83E\uDEE0', label: 'Drained', value: 'stressed' },
] as const

export function QuickCheckIn({ onCheckIn }: Props) {
  const [selected, setSelected] = useState<string | null>(null)
  const [confirmed, setConfirmed] = useState(false)

  const handleSelect = useCallback((mood: typeof MOODS[number]) => {
    if (confirmed) return
    setSelected(mood.value)
    setConfirmed(true)
    onCheckIn(mood.value, mood.label)

    setTimeout(() => {
      setSelected(null)
      setConfirmed(false)
    }, 3000)
  }, [confirmed, onCheckIn])

  return (
    <article className="soul-card p-6">
      <h3 className="text-sm font-semibold tracking-wide uppercase mb-1" style={{ color: 'var(--soul-text-muted)' }}>
        Quick Check-in
      </h3>
      <p className="text-sm mb-5" style={{ color: 'var(--soul-text-secondary)' }}>
        {confirmed ? 'Logged! Thanks for checking in.' : 'How are you feeling right now?'}
      </p>

      <div className="flex items-center justify-between gap-2">
        {MOODS.map((mood) => (
          <button
            key={mood.value}
            onClick={() => handleSelect(mood)}
            className="flex flex-col items-center gap-1.5 px-2 py-2 rounded-xl transition-all"
            style={{
              background: selected === mood.value
                ? 'var(--soul-accent-pale)'
                : 'transparent',
              border: selected === mood.value
                ? '1px solid var(--soul-accent-light)'
                : '1px solid transparent',
              opacity: confirmed && selected !== mood.value ? 0.4 : 1,
              cursor: confirmed ? 'default' : 'pointer',
            }}
          >
            <span className="text-2xl">{mood.emoji}</span>
            <span
              className="text-[10px] font-medium"
              style={{ color: selected === mood.value ? 'var(--soul-accent)' : 'var(--soul-text-muted)' }}
            >
              {mood.label}
            </span>
          </button>
        ))}
      </div>
    </article>
  )
}
