// Inline audio player for AI voice responses

import { useState, useRef, useCallback } from 'react'

interface Props {
  audio_base64: string
}

export function AudioPlayer({ audio_base64 }: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)

  const togglePlay = useCallback(() => {
    if (!audioRef.current) {
      const audio = new Audio(`data:audio/mpeg;base64,${audio_base64}`)
      audioRef.current = audio

      audio.addEventListener('timeupdate', () => {
        if (audio.duration) {
          setProgress((audio.currentTime / audio.duration) * 100)
        }
      })
      audio.addEventListener('ended', () => {
        setIsPlaying(false)
        setProgress(0)
      })
    }

    if (isPlaying) {
      audioRef.current.pause()
      setIsPlaying(false)
    } else {
      audioRef.current.play()
      setIsPlaying(true)
    }
  }, [audio_base64, isPlaying])

  return (
    <div
      className="flex items-center gap-2 mt-2 px-2.5 py-1.5 rounded-full cursor-pointer"
      style={{ background: 'var(--soul-surface-alt)' }}
      onClick={togglePlay}
    >
      {/* Play/pause icon */}
      <svg width="14" height="14" viewBox="0 0 24 24" fill="var(--soul-accent)">
        {isPlaying ? (
          <>
            <rect x="6" y="4" width="4" height="16" rx="1" />
            <rect x="14" y="4" width="4" height="16" rx="1" />
          </>
        ) : (
          <polygon points="5,3 19,12 5,21" />
        )}
      </svg>

      {/* Progress bar */}
      <div className="flex-1 h-1 rounded-full" style={{ background: 'var(--soul-border)' }}>
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${progress}%`, background: 'var(--soul-accent)' }}
        />
      </div>

      {/* Waveform bars (decorative) */}
      <div className="flex items-center gap-px">
        {[8, 14, 6, 12, 10, 8, 14].map((h, i) => (
          <div
            key={i}
            className="w-0.5 rounded-full"
            style={{
              height: isPlaying ? undefined : `${h}px`,
              background: 'var(--soul-accent-light)',
              animation: isPlaying ? `wave-bar 0.8s ease-in-out ${i * 0.1}s infinite` : 'none',
              minHeight: '4px',
              maxHeight: '14px',
            }}
          />
        ))}
      </div>
    </div>
  )
}