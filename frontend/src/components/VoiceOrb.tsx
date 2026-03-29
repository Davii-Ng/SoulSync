// Compact voice orb with breathing/listening animations

import type { OrbState } from '../types'

interface Props {
  state: OrbState
  onClick: () => void
}

export function VoiceOrb({ state, onClick }: Props) {
  const stateLabel: Record<OrbState, string> = {
    idle: 'Tap to speak',
    listening: 'Listening...',
    thinking: 'Thinking...',
    speaking: 'Speaking...',
  }

  const orbClass =
    state === 'listening' ? 'orb-listening' :
    state === 'thinking'  ? 'orb-thinking' :
    'orb-idle'

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={onClick}
        className={`relative w-40 h-40 md:w-48 md:h-48 rounded-full flex items-center justify-center cursor-pointer transition-transform hover:scale-102 active:scale-95 ${orbClass}`}
        style={{ background: 'linear-gradient(135deg, var(--soul-gradient-start), var(--soul-gradient-end))' }}
        aria-label={stateLabel[state]}
      >
        {/* Pulse ring (visible when listening) */}
        <div
          className="pulse-ring absolute w-40 h-40 md:w-48 md:h-48 rounded-full"
          style={{ border: '1.5px solid var(--soul-accent-light)' }}
        />

        {/* Mic icon */}
        {state === 'listening' ? (
          /* Stop icon when listening */
          <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : state === 'thinking' ? (
          /* Dots when thinking */
          <div className="flex gap-2">
            <span className="thinking-dot w-2 h-2 rounded-full bg-white" style={{ animation: 'thinking-dot 1.2s ease-in-out infinite' }} />
            <span className="thinking-dot w-2 h-2 rounded-full bg-white" style={{ animation: 'thinking-dot 1.2s ease-in-out infinite' }} />
            <span className="thinking-dot w-2 h-2 rounded-full bg-white" style={{ animation: 'thinking-dot 1.2s ease-in-out infinite' }} />
          </div>
        ) : (
          /* Mic icon default */
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <path d="M12 3a4 4 0 0 1 4 4v4a4 4 0 0 1-8 0V7a4 4 0 0 1 4-4z"/>
            <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
          </svg>
        )}
      </button>
      <span className="text-2xl font-medium" style={{ color: 'var(--soul-text)' }}>
        {stateLabel[state]}
      </span>
    </div>
  )
}