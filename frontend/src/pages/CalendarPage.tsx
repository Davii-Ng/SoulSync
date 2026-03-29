import type { SavedEvent } from '../types'

interface Props {
  events: SavedEvent[]
}

export function CalendarPage({ events }: Props) {
  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl section-heading" style={{ color: 'var(--soul-text)' }}>
          Calendar
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--soul-text-muted)' }}>
          Events and reminders captured from your conversations.
        </p>
      </div>

      {events.length === 0 ? (
        <div
          className="dashboard-card rounded-2xl border p-8 text-center"
          style={{ borderColor: 'var(--soul-border-light)' }}
        >
          <span className="material-symbols-outlined text-5xl mb-3" style={{ color: 'var(--soul-accent-light)' }}>
            calendar_month
          </span>
          <p className="text-base font-medium" style={{ color: 'var(--soul-text-secondary)' }}>
            No events yet
          </p>
          <p className="text-sm mt-1" style={{ color: 'var(--soul-text-muted)' }}>
            Mention a date, deadline, or appointment while speaking and SoulSync will save it here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {events.map((event) => (
            <article
              key={event.id}
              className="dashboard-card dashboard-card-hover rounded-2xl border p-5"
              style={{ borderColor: 'var(--soul-border-light)' }}
            >
              <div className="flex items-start gap-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                  style={{ background: 'var(--soul-accent-pale)' }}
                >
                  <span className="material-symbols-outlined text-lg" style={{ color: 'var(--soul-accent)' }}>
                    event
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold" style={{ color: 'var(--soul-text)' }}>
                    {event.title}
                  </h3>
                  <p className="text-xs mt-1 font-medium" style={{ color: 'var(--soul-accent)' }}>
                    {event.dateLabel}
                  </p>
                  {event.note && (
                    <p className="text-xs mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                      {event.note}
                    </p>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}
