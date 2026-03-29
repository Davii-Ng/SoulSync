// App header with brand, tagline, and user pill

interface Props {
  isConnected: boolean
}

export function Header({ isConnected }: Props) {
  return (
    <header
      className="dashboard-strip rounded-xl border px-5 py-4"
      style={{ borderColor: 'var(--soul-border-light)', background: 'var(--soul-surface)' }}
    >
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight" style={{ color: 'var(--soul-text)' }}>
          SoulSync
        </h1>

        <p className="text-base hidden md:block" style={{ color: 'var(--soul-text-secondary)' }}>
          Feel heard. Feel better.
        </p>

        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
          <button
            type="button"
            className="px-4 py-1.5 rounded-full text-sm border"
            style={{ borderColor: 'var(--soul-border)', color: 'var(--soul-text-secondary)' }}
          >
            avatar
          </button>
        </div>
      </div>
    </header>
  )
}