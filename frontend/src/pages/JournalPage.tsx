import { useState } from 'react'
import type { JournalEntry } from '../types'
import { EMOTION_CONFIG } from '../utils/constants'

interface Props {
  journals: JournalEntry[]
}

export function JournalPage({ journals }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  // Sort by date descending
  const sorted = [...journals].sort((a, b) => b.date.localeCompare(a.date))

  const toggle = (id: string) =>
    setExpandedId((prev) => (prev === id ? null : id))

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl section-heading text-soul-text">Journal</h1>
        <p className="text-sm mt-1 text-soul-text-muted">
          Your daily conversations, saved and organized.
        </p>
      </div>

      {sorted.length === 0 ? (
        <div className="dashboard-card rounded-2xl border border-soul-border-light p-8 text-center">
          <span className="material-symbols-outlined text-5xl mb-3 text-soul-accent-light">
            auto_stories
          </span>
          <p className="text-base font-medium text-soul-text-secondary">
            No journal entries yet
          </p>
          <p className="text-sm mt-1 text-soul-text-muted">
            Tell SoulSync "save today's journal" when you're done chatting.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {sorted.map((entry) => {
            const isOpen = expandedId === entry.id
            const date = new Date(entry.date + 'T00:00:00')
            const dateStr = date.toLocaleDateString([], {
              weekday: 'long',
              month: 'long',
              day: 'numeric',
              year: 'numeric',
            })
            const msgCount = entry.messages.length
            // Find dominant emotion from assistant messages
            const emotions = entry.messages
              .filter((m) => m.role === 'assistant' && m.emotion)
              .map((m) => m.emotion!)
            const dominant = emotions.length > 0 ? mostCommon(emotions) : null
            const emotionStyle = dominant ? EMOTION_CONFIG[dominant] : null

            return (
              <article
                key={entry.id}
                className="dashboard-card rounded-2xl border border-soul-border-light overflow-hidden"
              >
                {/* Collapsible header */}
                <button
                  type="button"
                  onClick={() => toggle(entry.id)}
                  className="w-full flex items-center justify-between p-5 md:p-6 text-left hover:bg-soul-surface-alt transition-colors"
                >
                  <div className="flex flex-col gap-1">
                    <span className="text-sm font-semibold text-soul-text">
                      {dateStr}
                    </span>
                    <span className="text-xs text-soul-text-muted">
                      {msgCount} message{msgCount !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {emotionStyle && (
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${emotionStyle.bg} ${emotionStyle.color}`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${emotionStyle.dot}`} />
                        {emotionStyle.label}
                      </span>
                    )}
                    <span
                      className={`material-symbols-outlined text-lg text-soul-text-muted transition-transform ${
                        isOpen ? 'rotate-180' : ''
                      }`}
                    >
                      expand_more
                    </span>
                  </div>
                </button>

                {/* Expandable conversation body */}
                {isOpen && (
                  <div className="border-t border-soul-border px-5 md:px-6 py-4 flex flex-col gap-3">
                    {entry.messages.map((msg) => {
                      const time = new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                      const isUser = msg.role === 'user'
                      return (
                        <div
                          key={msg.id}
                          className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
                        >
                          <div
                            className={`max-w-[85%] px-4 py-2.5 text-sm leading-relaxed ${
                              isUser ? 'bubble-user' : 'bubble-ai'
                            }`}
                          >
                            {msg.content}
                          </div>
                          <span className="text-[0.65rem] mt-0.5 text-soul-text-muted">
                            {time}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                )}
              </article>
            )
          })}
        </div>
      )}
    </div>
  )
}

/** Return the most frequent item in an array. */
function mostCommon<T>(arr: T[]): T {
  const counts = new Map<T, number>()
  for (const item of arr) counts.set(item, (counts.get(item) || 0) + 1)
  let best = arr[0]
  let max = 0
  for (const [item, count] of counts) {
    if (count > max) { best = item; max = count }
  }
  return best
}
