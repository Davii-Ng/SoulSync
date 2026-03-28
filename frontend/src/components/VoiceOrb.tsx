// Animated circle centerpiece, mic control with pulse animation

import type { OrbState } from '../types'

interface Props {
  state: OrbState
  onClick: () => void
}

export function VoiceOrb({ state, onClick }: Props) {
  const stateLabel = {
    idle: 'Tap to speak',
    listening: 'Listening...',
    thinking: 'Thinking...',
    speaking: 'Speaking...',
  }
  
  const isActive = state === 'listening'

  return (
    <div className="flex flex-col items-center gap-4 py-10">
      <button
        onClick={onClick}
        className={`relative w-40 h-40 rounded-full flex items-center justify-center cursor-pointer transition-all hover:scale-105 ${isActive ? 'orb-listening' : ''}`}
      >
        <div className="pulse-ring absolute w-40 h-40 rounded-full border border-purple-500/40" />
        <div className="w-40 h-40 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
          <div className="orb-inner w-24 h-24 rounded-full bg-purple-500/40" />
        </div>
      </button>
      <p className="text-sm text-gray-400">{stateLabel[state]}</p>
    </div>
  )
}