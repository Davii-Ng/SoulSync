import type { SavedEvent, AppTab } from '../types'

interface Props {
  events: SavedEvent[]
  activeTab: AppTab
}

export function EventsPanel({ events, activeTab }: Props) {
  const title = activeTab === 'calendar'
    ? 'Saved Events'
    : activeTab === 'resources'
      ? 'Suggested Resources'
      : 'Context Panel'

  const subtitle = activeTab === 'calendar'
    ? 'Items your AI companion captured from your conversation'
    : activeTab === 'resources'
      ? 'Helpful follow-ups from your recent check-ins'
      : 'Calendar and resource previews appear here'

  return (
    <aside
      className="flex flex-col border-t md:border-t-0 md:border-l"
      style={{ borderColor: 'var(--soul-border-light)', background: 'var(--soul-surface)' }}
    >
      <div className="px-5 py-4 border-b" style={{ borderColor: 'var(--soul-border-light)' }}>
        <h2 className="text-sm font-semibold" style={{ color: 'var(--soul-text)' }}>
          {title}
        </h2>
        <p className="text-xs mt-1" style={{ color: 'var(--soul-text-muted)' }}>
          {subtitle}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 min-h-[180px]">
        {events.length === 0 ? (
          <div
            className="rounded-2xl border p-4"
            style={{ borderColor: 'var(--soul-border-light)', background: 'var(--soul-surface-alt)' }}
          >
            <p className="text-sm font-medium" style={{ color: 'var(--soul-text-secondary)' }}>
              No saved events yet
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--soul-text-muted)' }}>
              Mention a date, deadline, or appointment and SoulSync can keep track of it here.
            </p>
          </div>
        ) : (
          events.map((event) => (
            <article
              key={event.id}
              className="rounded-2xl border p-4"
              style={{ borderColor: 'var(--soul-border-light)', background: 'var(--soul-surface-alt)' }}
            >
              <h3 className="text-sm font-semibold" style={{ color: 'var(--soul-text)' }}>
                {event.title}
              </h3>
              <p className="text-xs mt-1" style={{ color: 'var(--soul-text-secondary)' }}>
                {event.dateLabel}
              </p>
              {event.note ? (
                <p className="text-xs mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                  {event.note}
                </p>
              ) : null}
            </article>
          ))
        )}
      </div>
    </aside>
  )
}
