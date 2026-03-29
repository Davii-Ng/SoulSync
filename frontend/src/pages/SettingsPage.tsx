import { useEffect, useState, useRef } from 'react'
import { API_URL } from '../utils/constants'
import type { Voice } from '../types'

interface SettingsPageProps {
  selectedVoiceId: string | null
  onVoiceChange: (voiceId: string | null) => void
}

export function SettingsPage({ selectedVoiceId, onVoiceChange }: SettingsPageProps) {
  const [voices, setVoices] = useState<Voice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [previewingId, setPreviewingId] = useState<string | null>(null)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  useEffect(() => {
    fetch(`${API_URL}/voices`)
      .then((res) => res.json())
      .then((data) => {
        if (data.success) setVoices(data.voices)
        else setError('Failed to load voices.')
      })
      .catch(() => setError('Could not connect to server.'))
      .finally(() => setLoading(false))
  }, [])

  const handlePreview = async (voiceId: string) => {
    // Stop any current preview
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    setPreviewingId(voiceId)
    setPreviewError(null)
    try {
      const res = await fetch(`${API_URL}/voices/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: voiceId }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => null)
        throw new Error(data?.error || 'Preview failed')
      }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)
      audioRef.current = audio
      audio.onended = () => {
        setPreviewingId(null)
        URL.revokeObjectURL(url)
      }
      await audio.play()
    } catch (e) {
      setPreviewingId(null)
      setPreviewError(e instanceof Error ? e.message : 'Preview unavailable')
    }
  }

  const handleSelect = (voiceId: string) => {
    const newId = voiceId === selectedVoiceId ? null : voiceId
    onVoiceChange(newId)
  }

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
        className="dashboard-card rounded-2xl border p-6"
        style={{ borderColor: 'var(--soul-border-light)' }}
      >
        <div className="flex items-center gap-2 mb-4">
          <span
            className="material-symbols-outlined text-2xl"
            style={{ color: 'var(--soul-accent)' }}
          >
            record_voice_over
          </span>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--soul-text)' }}>
            Voice Selection
          </h2>
        </div>
        <p className="text-sm mb-4" style={{ color: 'var(--soul-text-muted)' }}>
          Choose the voice SoulSync uses when speaking to you.
          {selectedVoiceId ? '' : ' Using default voice.'}
        </p>

        {previewError && (
          <p className="text-sm mb-3 px-3 py-2 rounded-lg" style={{ color: '#dc2626', background: 'rgba(220, 38, 38, 0.08)' }}>
            {previewError}
          </p>
        )}

        {loading && (
          <p className="text-sm" style={{ color: 'var(--soul-text-muted)' }}>
            Loading voices...
          </p>
        )}

        {error && (
          <p className="text-sm" style={{ color: 'var(--soul-error, #ef4444)' }}>
            {error}
          </p>
        )}

        {!loading && !error && (
          <div className="grid gap-2" style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {voices.map((voice) => {
              const isSelected = voice.voice_id === selectedVoiceId
              const isPreviewing = voice.voice_id === previewingId
              return (
                <div
                  key={voice.voice_id}
                  className="flex items-center justify-between rounded-xl border px-4 py-3 transition-all"
                  style={{
                    borderColor: isSelected
                      ? 'var(--soul-accent)'
                      : 'var(--soul-border-light)',
                    background: isSelected
                      ? 'var(--soul-accent-bg, rgba(139, 92, 246, 0.08))'
                      : 'transparent',
                  }}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className="material-symbols-outlined text-xl"
                      style={{
                        color: isSelected
                          ? 'var(--soul-accent)'
                          : 'var(--soul-text-muted)',
                      }}
                    >
                      {isSelected ? 'check_circle' : 'radio_button_unchecked'}
                    </span>
                    <span
                      className="text-sm font-medium"
                      style={{ color: 'var(--soul-text)' }}
                    >
                      {voice.name}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handlePreview(voice.voice_id)}
                      disabled={isPreviewing}
                      className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors"
                      style={{
                        background: 'var(--soul-border-light)',
                        color: 'var(--soul-text-secondary)',
                        opacity: isPreviewing ? 0.6 : 1,
                        cursor: isPreviewing ? 'not-allowed' : 'pointer',
                      }}
                    >
                      <span className="material-symbols-outlined text-base">
                        {isPreviewing ? 'volume_up' : 'play_arrow'}
                      </span>
                      {isPreviewing ? 'Playing...' : 'Preview'}
                    </button>

                    <button
                      onClick={() => handleSelect(voice.voice_id)}
                      className="rounded-lg px-3 py-1.5 text-xs font-medium transition-colors"
                      style={{
                        background: isSelected
                          ? 'var(--soul-accent)'
                          : 'var(--soul-border-light)',
                        color: isSelected ? '#fff' : 'var(--soul-text-secondary)',
                      }}
                    >
                      {isSelected ? 'Selected' : 'Select'}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
