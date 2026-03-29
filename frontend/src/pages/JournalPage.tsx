import type { Message } from '../types'
import { EMOTION_CONFIG } from '../utils/constants'

interface Props {
  messages: Message[]
}

export function JournalPage({ messages }: Props) {
  const entries = messages.filter((m) => m.role === 'user')

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl section-heading" style={{ color: 'var(--soul-text)' }}>
          Journal
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--soul-text-muted)' }}>
          Your reflections and conversations, saved here.
        </p>
      </div>

      {entries.length === 0 ? (
        <div
          className="dashboard-card rounded-2xl border p-8 text-center"
          style={{ borderColor: 'var(--soul-border-light)' }}
        >
          <span className="material-symbols-outlined text-5xl mb-3" style={{ color: 'var(--soul-accent-light)' }}>
            auto_stories
          </span>
          <p className="text-base font-medium" style={{ color: 'var(--soul-text-secondary)' }}>
            No journal entries yet
          </p>
          <p className="text-sm mt-1" style={{ color: 'var(--soul-text-muted)' }}>
            Start a conversation on the Speaking page and your entries will appear here.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {entries.map((entry) => {
            const emotion = entry.emotion
            const emotionStyle = emotion ? EMOTION_CONFIG[emotion] : null
            const date = new Date(entry.timestamp)
            const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' })

            return (
              <article
                key={entry.id}
                className="dashboard-card dashboard-card-hover rounded-2xl border p-5"
                style={{ borderColor: 'var(--soul-border-light)' }}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-medium" style={{ color: 'var(--soul-text-muted)' }}>
                    {dateStr} at {timeStr}
                  </span>
                  {emotionStyle && (
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${emotionStyle.bg} ${emotionStyle.color}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${emotionStyle.dot}`} />
                      {emotionStyle.label}
                    </span>
                  )}
                </div>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--soul-text)' }}>
                  {entry.content}
                </p>
                {entry.isVoice && (
                  <span className="inline-flex items-center gap-1 mt-2 text-xs" style={{ color: 'var(--soul-text-muted)' }}>
                    <span className="material-symbols-outlined text-sm">mic</span>
                    Voice entry
                  </span>
                )}
              </article>
            )
          })}
        </div>
      )}
    </div>
  )
}
