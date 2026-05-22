import { Link } from 'react-router-dom'
import type { Emotion, JournalEntry, SavedEvent } from '../types'
import { EMOTION_CONFIG } from '../utils/constants'

interface Props {
  emotion: Emotion
  savedJournals: JournalEntry[]
  savedEvents: SavedEvent[]
}

function getGreeting(): string {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

export function HomePage({ emotion, savedJournals, savedEvents }: Props) {
  const config = EMOTION_CONFIG[emotion] ?? EMOTION_CONFIG.neutral
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })

  return (
    <div className="flex flex-col gap-5">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl section-heading text-soul-text">{getGreeting()}</h1>
        <p className="text-sm mt-1 text-soul-text-muted">{today}</p>
      </div>

      {/* Current emotion */}
      <div className={`dashboard-card rounded-2xl border border-soul-border-light p-5 flex items-center gap-4 ${config.bg}`}>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${config.bg}`}>
          <span className={`material-symbols-outlined text-2xl ${config.color}`}>
            sentiment_satisfied
          </span>
        </div>
        <div>
          <p className="text-xs text-soul-text-muted font-medium uppercase tracking-wide">Right now you feel</p>
          <span className={`text-lg font-semibold ${config.color}`}>{config.label}</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="dashboard-card rounded-2xl border border-soul-border-light p-5 flex flex-col gap-1">
          <span className="text-2xl font-bold text-soul-text">{savedJournals.length}</span>
          <span className="text-xs text-soul-text-muted">Journal entries</span>
        </div>
        <div className="dashboard-card rounded-2xl border border-soul-border-light p-5 flex flex-col gap-1">
          <span className="text-2xl font-bold text-soul-text">{savedEvents.length}</span>
          <span className="text-xs text-soul-text-muted">Saved events</span>
        </div>
      </div>

      {/* Quick actions */}
      <div className="dashboard-card rounded-2xl border border-soul-border-light p-5 md:p-6">
        <h3 className="text-sm font-semibold mb-4 text-soul-text">Quick actions</h3>
        <div className="flex flex-col gap-2">
          <Link
            to="/"
            className="flex items-center gap-3 px-4 py-3 rounded-xl bg-soul-accent-pale hover:bg-soul-accent-light/20 transition-colors"
          >
            <span className="material-symbols-outlined text-xl text-soul-accent">mic</span>
            <span className="text-sm font-medium text-soul-text">Start speaking</span>
          </Link>
          <Link
            to="/journal"
            className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-soul-accent-pale transition-colors"
          >
            <span className="material-symbols-outlined text-xl text-soul-text-secondary">auto_stories</span>
            <span className="text-sm font-medium text-soul-text">View journal</span>
          </Link>
          <Link
            to="/calendar"
            className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-soul-accent-pale transition-colors"
          >
            <span className="material-symbols-outlined text-xl text-soul-text-secondary">calendar_month</span>
            <span className="text-sm font-medium text-soul-text">View calendar</span>
          </Link>
          <Link
            to="/resources"
            className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-soul-accent-pale transition-colors"
          >
            <span className="material-symbols-outlined text-xl text-soul-text-secondary">health_and_safety</span>
            <span className="text-sm font-medium text-soul-text">Resources</span>
          </Link>
        </div>
      </div>
    </div>
  )
}
