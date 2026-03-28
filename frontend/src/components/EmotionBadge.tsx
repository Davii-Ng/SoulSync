import type { Emotion } from '../types'
import { EMOTION_CONFIG } from '../utils/constants'

interface Props {
  emotion: Emotion
}

export function EmotionBadge({ emotion }: Props) {
  const config = EMOTION_CONFIG[emotion]

  return (
    <div className="flex justify-center px-6 py-2">
      <span className={`px-4 py-1.5 rounded-full bg-white/5 text-sm ${config.color}`}>
        {config.label}
      </span>
    </div>
  )
}