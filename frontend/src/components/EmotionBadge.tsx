// Compact emotion badge with colored dot

import type { Emotion } from '../types'
import { EMOTION_CONFIG } from '../utils/constants'

interface Props {
  emotion: Emotion
}

export function EmotionBadge({ emotion }: Props) {
  const config = EMOTION_CONFIG[emotion]

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  )
}