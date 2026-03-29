// App header with brand, tagline, and user pill

interface Props {
  isConnected: boolean
}

export function Header({ isConnected }: Props) {
  return (
    <header className="dashboard-strip header-shell rounded-2xl border border-soul-border-light bg-soul-surface px-5 py-3.5 md:px-6">
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
        <div className="flex items-center gap-3">
          <span className="header-spark" aria-hidden="true" />
          <h1 className="text-2xl header-title text-soul-text">
            SoulSync
          </h1>
        </div>

        <p className="text-base text-center header-tagline text-soul-text-secondary">
          Feel heard. Feel better.
        </p>

        <div className="flex items-center gap-2 justify-self-end">
          <span
            className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
          <button
            type="button"
            className="w-9 h-9 rounded-full flex items-center justify-center text-sm header-avatar border-soul-border text-soul-text-secondary"
            aria-label="User profile"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="8" r="4"/>
              <path d="M20 21a8 8 0 0 0-16 0"/>
            </svg>
          </button>
        </div>
      </div>
    </header>
  )
}
