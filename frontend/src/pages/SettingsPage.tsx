export function SettingsPage() {
  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl section-heading" style={{ color: 'var(--soul-text)' }}>
          Settings
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--soul-text-muted)' }}>
          Preferences and account configuration.
        </p>
      </div>

      <div
        className="dashboard-card rounded-2xl border p-8 text-center"
        style={{ borderColor: 'var(--soul-border-light)' }}
      >
        <span className="material-symbols-outlined text-5xl mb-3" style={{ color: 'var(--soul-accent-light)' }}>
          settings
        </span>
        <p className="text-base font-medium" style={{ color: 'var(--soul-text-secondary)' }}>
          Coming soon
        </p>
        <p className="text-sm mt-1" style={{ color: 'var(--soul-text-muted)' }}>
          Theme, notifications, and account settings will appear here.
        </p>
      </div>
    </div>
  )
}
