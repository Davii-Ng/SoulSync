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

  return (
    <div className="flex flex-col items-center gap-4 py-10">
      <button
        onClick={onClick}
        className="w-40 h-40 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center cursor-pointer transition-all hover:bg-purple-500/30 hover:scale-105"
      >
        <div className="w-24 h-24 rounded-full bg-purple-500/40" />
      </button>
      <p className="text-sm text-gray-400">{stateLabel[state]}</p>
    </div>
  )
}