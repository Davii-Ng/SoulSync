// Compact voice orb with breathing/listening animations

import type { OrbState } from '../../types'

interface Props {
  state: OrbState
  onClick: () => void
  transcript?: string
}

export function VoiceOrb({ state, onClick, transcript }: Props) {
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
    <div className="flex flex-col items-center gap-3">
      <h1></h1>
      <button
        onClick={onClick}
        className={`relative w-40 h-40 md:w-48 md:h-48 rounded-full flex items-center justify-center cursor-pointer transition-transform hover:scale-105 active:scale-95 bg-soul-accent ${orbClass}`}
        aria-label={stateLabel[state]}
      >
        {/* Pulse ring (visible when listening) */}
        <div className="pulse-ring absolute w-40 h-40 md:w-48 md:h-48 rounded-full" />

        {/* Mic icon */}
        {state === 'listening' ? (
          <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : state === 'thinking' ? (
          <div className="flex gap-2">
            <span className="thinking-dot w-2 h-2 rounded-full bg-slate-500" style={{ animation: 'thinking-dot 1.2s ease-in-out infinite' }} />
            <span className="thinking-dot w-2 h-2 rounded-full bg-slate-500" style={{ animation: 'thinking-dot 1.2s ease-in-out infinite' }} />
            <span className="thinking-dot w-2 h-2 rounded-full bg-slate-500" style={{ animation: 'thinking-dot 1.2s ease-in-out infinite' }} />
          </div>
        ) : (
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <path d="M12 3a4 4 0 0 1 4 4v4a4 4 0 0 1-8 0V7a4 4 0 0 1 4-4z"/>
            <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
          </svg>
        )}
      </button>
      <span className="text-sm tech-font mt-2 text-soul-text-secondary">
        {stateLabel[state].toUpperCase()}
      </span>
      {state === 'listening' && transcript && (
        <p className="text-sm max-w-xs text-center mt-1 italic text-soul-text-secondary">
          {transcript}
        </p>
      )}
    </div>
  )
}
