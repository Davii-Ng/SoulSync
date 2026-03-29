import { useEffect, useState, useRef, useMemo } from 'react'
import { API_URL } from '../utils/constants'
import type { Voice } from '../types'

type GenderFilter = 'all' | 'male' | 'female'
type SortOption = 'name' | 'gender'

interface SettingsPageProps {
  selectedVoiceId: string | null
  onVoiceChange: (voiceId: string | null, voiceName: string | null) => void
}

export function SettingsPage({ selectedVoiceId, onVoiceChange }: SettingsPageProps) {
  const [voices, setVoices] = useState<Voice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [previewingId, setPreviewingId] = useState<string | null>(null)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [genderFilter, setGenderFilter] = useState<GenderFilter>('all')
  const [sortBy, setSortBy] = useState<SortOption>('name')
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

  const filteredVoices = useMemo(() => {
    let result = voices
    if (genderFilter !== 'all') {
      result = result.filter((v) => v.gender === genderFilter)
    }
    return result.slice().sort((a, b) => {
      if (sortBy === 'gender') {
        const order = { female: 0, male: 1, unknown: 2 }
        const diff = (order[a.gender] ?? 2) - (order[b.gender] ?? 2)
        if (diff !== 0) return diff
      }
      return a.name.localeCompare(b.name)
    })
  }, [voices, genderFilter, sortBy])

  const handlePreview = async (voice: Voice) => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    setPreviewingId(voice.voice_id)
    setPreviewError(null)
    try {
      const res = await fetch(`${API_URL}/voices/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: voice.voice_id, voice_name: voice.name }),
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

  const handleSelect = (voice: Voice) => {
    const isDeselect = voice.voice_id === selectedVoiceId
    onVoiceChange(isDeselect ? null : voice.voice_id, isDeselect ? null : voice.name)
  }


  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-3xl section-heading text-soul-text">
          Settings
        </h1>
        <p className="text-sm mt-1 text-soul-text-muted">
          Preferences and account configuration.
        </p>
      </div>

      <div className="dashboard-card rounded-2xl border border-soul-border-light p-6 md:p-8">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined text-2xl text-soul-accent">
            record_voice_over
          </span>
          <h2 className="text-lg font-semibold text-soul-text">
            Voice Selection
          </h2>
        </div>
        <p className="text-sm mb-4 text-soul-text-muted">
          Choose the voice SoulSync uses when speaking to you.
          {selectedVoiceId ? '' : ' Using default voice.'}
        </p>

        {/* Filter & Sort controls */}
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-soul-text-secondary">
              Filter:
            </span>
            {(['all', 'female', 'male'] as GenderFilter[]).map((g) => (
              <button
                key={g}
                onClick={() => setGenderFilter(g)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  genderFilter === g
                    ? 'bg-soul-accent text-white'
                    : 'bg-soul-border-light text-soul-text-secondary'
                }`}
              >
                {g === 'all' ? 'All' : g === 'female' ? 'Female' : 'Male'}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-soul-text-secondary">
              Sort:
            </span>
            {(['name', 'gender'] as SortOption[]).map((s) => (
              <button
                key={s}
                onClick={() => setSortBy(s)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  sortBy === s
                    ? 'bg-soul-accent text-white'
                    : 'bg-soul-border-light text-soul-text-secondary'
                }`}
              >
                {s === 'name' ? 'Name' : 'Gender'}
              </button>
            ))}
          </div>
          {!loading && !error && (
            <span className="text-xs ml-auto text-soul-text-muted">
              {filteredVoices.length} voice{filteredVoices.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        {previewError && (
          <p className="text-sm mb-3 px-3 py-2 rounded-lg text-soul-error bg-red-50">
            {previewError}
          </p>
        )}

        {loading && (
          <p className="text-sm text-soul-text-muted">
            Loading voices...
          </p>
        )}

        {error && (
          <p className="text-sm text-soul-error">
            {error}
          </p>
        )}

        {!loading && !error && (
          <div className="grid gap-2 max-h-[400px] overflow-y-auto">
            {filteredVoices.map((voice) => {
              const isSelected = voice.voice_id === selectedVoiceId
              const isPreviewing = voice.voice_id === previewingId
              return (
                <div
                  key={voice.voice_id}
                  className={`flex items-center justify-between rounded-xl border px-5 py-3.5 transition-all ${
                    isSelected
                      ? 'border-soul-accent bg-soul-accent-pale'
                      : 'border-soul-border-light bg-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`material-symbols-outlined text-xl ${
                        isSelected ? 'text-soul-accent' : 'text-soul-text-muted'
                      }`}
                    >
                      {isSelected ? 'check_circle' : 'radio_button_unchecked'}
                    </span>
                    <span className="text-sm font-medium text-soul-text">
                      {voice.name}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handlePreview(voice)}
                      disabled={isPreviewing}
                      className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors bg-soul-border-light text-soul-text-secondary ${
                        isPreviewing ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'
                      }`}
                    >
                      <span className="material-symbols-outlined text-base">
                        {isPreviewing ? 'volume_up' : 'play_arrow'}
                      </span>
                      {isPreviewing ? 'Playing...' : 'Preview'}
                    </button>

                    <button
                      onClick={() => handleSelect(voice)}
                      className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                        isSelected
                          ? 'bg-soul-accent text-white'
                          : 'bg-soul-border-light text-soul-text-secondary'
                      }`}
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
