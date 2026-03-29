// App header with logo and emotion badge

import type { Emotion } from '../types'
import { EmotionBadge } from './EmotionBadge'

interface Props {
  emotion: Emotion
  isConnected: boolean
}

export function Header({ emotion, isConnected }: Props) {
  return (
    <header className="flex items-center justify-between px-5 py-3.5 border-b"
      style={{ borderColor: 'var(--soul-border-light)', background: 'var(--soul-surface)' }}>
      <div className="flex items-center gap-2.5">
        {/* Logo orb */}
        <div className="w-9 h-9 rounded-full flex items-center justify-center"
          style={{ background: 'linear-gradient(135deg, var(--soul-gradient-start), var(--soul-gradient-end))' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <path d="M12 3a4 4 0 0 1 4 4v4a4 4 0 0 1-8 0V7a4 4 0 0 1 4-4z"/>
            <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
            <line x1="12" y1="19" x2="12" y2="22"/>
          </svg>
        </div>
        <div>
          <h1 className="text-base font-semibold" style={{ color: 'var(--soul-text)' }}>
            SoulSync
          </h1>
          <div className="flex items-center gap-1.5">
            <span className="text-xs" style={{ color: 'var(--soul-text-muted)' }}>
              Feel heard. Feel better.
            </span>
            {/* Connection dot */}
            <span
              className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}
              title={isConnected ? 'Connected' : 'Disconnected'}
            />
          </div>
        </div>
      </div>
      <EmotionBadge emotion={emotion} />
    </header>
  )
}