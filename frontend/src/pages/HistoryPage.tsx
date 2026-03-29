import type { Message } from '../types'
import { EMOTION_CONFIG } from '../utils/constants'

interface Props {
  messages: Message[]
}

const MOOD_ICONS: Record<string, string> = {
  calm: 'sentiment_satisfied',
  stressed: 'sentiment_stressed',
  anxious: 'psychology',
  happy: 'sentiment_very_satisfied',
  sad: 'sentiment_dissatisfied',
  angry: 'sentiment_extremely_dissatisfied',
  neutral: 'sentiment_neutral',
}

export function HistoryPage({ messages }: Props) {
  // Build mood timeline from assistant messages that have emotions
  const moodEntries = messages
    .filter((m) => m.emotion)
    .map((m) => ({
      id: m.id,
      emotion: m.emotion!,
      timestamp: m.timestamp,
      snippet: m.content.slice(0, 80) + (m.content.length > 80 ? '...' : ''),
    }))

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl section-heading text-soul-text">
          Mood History
        </h1>
        <p className="text-sm mt-1 text-soul-text-muted">
          Track how your emotions have evolved over your sessions.
        </p>
      </div>

      {/* Weekly overview */}
      <div className="dashboard-card rounded-2xl border border-soul-border-light p-5 md:p-6">
        <h3 className="text-sm font-semibold mb-4 text-soul-text">
          This Week
        </h3>
        <div className="flex items-end justify-around gap-2">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => {
            const heights = [40, 55, 35, 60, 45, 70, 50]
            const colors = ['bg-teal-400', 'bg-blue-400', 'bg-amber-400', 'bg-green-400', 'bg-orange-400', 'bg-teal-400', 'bg-blue-400']
            return (
              <div key={day} className="flex flex-col items-center gap-2">
                <div
                  className={`w-8 rounded-lg ${colors[i]} transition-all opacity-70`}
                  style={{ height: `${heights[i]}px` }}
                />
                <span className="text-xs text-soul-text-muted">
                  {day}
                </span>
              </div>
            )
          })}
        </div>
        <p className="text-xs mt-4 text-soul-text-muted">
          Mostly positive this week
        </p>
      </div>

      {/* Timeline */}
      {moodEntries.length === 0 ? (
        <div className="dashboard-card rounded-2xl border border-soul-border-light p-8 text-center">
          <span className="material-symbols-outlined text-5xl mb-3 text-soul-accent-light">
            timeline
          </span>
          <p className="text-base font-medium text-soul-text-secondary">
            No mood data yet
          </p>
          <p className="text-sm mt-1 text-soul-text-muted">
            As you talk with SoulSync, your emotional journey will be tracked here.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {moodEntries.reverse().map((entry) => {
            const config = EMOTION_CONFIG[entry.emotion]
            const date = new Date(entry.timestamp)
            const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

            return (
              <div
                key={entry.id}
                className="dashboard-card rounded-2xl border border-soul-border-light p-5 md:p-6 flex items-start gap-3"
              >
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${config.bg}`}
                >
                  <span className={`material-symbols-outlined text-lg ${config.color}`}>
                    {MOOD_ICONS[entry.emotion] || 'sentiment_neutral'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
                      {config.label}
                    </span>
                    <span className="text-xs text-soul-text-muted">
                      {timeStr}
                    </span>
                  </div>
                  <p className="text-xs mt-1.5 leading-relaxed text-soul-text-secondary">
                    {entry.snippet}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
