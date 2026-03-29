// App header with brand, tagline, and user pill

interface Props {
  isConnected: boolean
}

export function Header({ isConnected }: Props) {
  return (
    <header
      className="dashboard-strip header-shell rounded-xl border px-5 py-3.5 md:px-6"
      style={{ borderColor: 'var(--soul-border-light)', background: 'var(--soul-surface)' }}
    >
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
        <div className="flex items-center gap-3">
          <span className="header-spark" aria-hidden="true" />
          <h1 className="text-2xl header-title" style={{ color: 'var(--soul-text)' }}>
            SoulSync
          </h1>
        </div>

        <p className="text-base text-center header-tagline" style={{ color: 'var(--soul-text-secondary)' }}>
          Feel heard. Feel better.
        </p>

        <div className="flex items-center gap-2 justify-self-end">
          <span
            className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
          <button
            type="button"
            className="px-4 py-1.5 rounded-full text-sm header-avatar"
            style={{ borderColor: 'var(--soul-border)', color: 'var(--soul-text-secondary)' }}
          >
            avatar
          </button>
        </div>
      </div>
    </header>
  )
}