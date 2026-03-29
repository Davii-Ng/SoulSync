import { useState, useEffect, useRef, useCallback } from 'react'
import type { Emotion } from '../types'

interface Props {
  emotion: Emotion
  aiSuggested: boolean
}

type ActiveTool = null | 'breathing' | 'grounding'

const BREATHING_PHASES = [
  { label: 'Inhale', duration: 4 },
  { label: 'Hold', duration: 4 },
  { label: 'Exhale', duration: 4 },
  { label: 'Hold', duration: 4 },
] as const

const GROUNDING_STEPS = [
  { count: 5, sense: 'SEE', prompt: 'Name 5 things you can see' },
  { count: 4, sense: 'TOUCH', prompt: 'Name 4 things you can touch' },
  { count: 3, sense: 'HEAR', prompt: 'Name 3 things you can hear' },
  { count: 2, sense: 'SMELL', prompt: 'Name 2 things you can smell' },
  { count: 1, sense: 'TASTE', prompt: 'Name 1 thing you can taste' },
] as const

function BreathingGuide({ onClose }: { onClose: () => void }) {
  const [phase, setPhase] = useState(0)
  const [seconds, setSeconds] = useState<number>(BREATHING_PHASES[0].duration)
  const [cycles, setCycles] = useState(0)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setSeconds((s) => {
        if (s <= 1) {
          setPhase((p) => {
            const next = (p + 1) % BREATHING_PHASES.length
            if (next === 0) setCycles((c) => c + 1)
            return next
          })
          return BREATHING_PHASES[(phase + 1) % BREATHING_PHASES.length].duration
        }
        return s - 1
      })
    }, 1000)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [phase])

  const current = BREATHING_PHASES[phase]
  const progress = 1 - (seconds - 1) / current.duration
  const isExpanding = phase === 0
  const scale = isExpanding ? 0.6 + progress * 0.4 : phase === 2 ? 1 - progress * 0.4 : phase === 1 ? 1 : 0.6

  return (
    <div className="mt-3 rounded-xl p-4" style={{ background: 'var(--soul-surface-alt)', border: '1px solid var(--soul-border-light)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium" style={{ color: 'var(--soul-text-muted)' }}>
          Cycle {cycles + 1}
        </span>
        <button
          onClick={onClose}
          className="text-xs px-2 py-0.5 rounded-full"
          style={{ color: 'var(--soul-text-muted)', background: 'var(--soul-surface)' }}
        >
          Close
        </button>
      </div>

      <div className="flex flex-col items-center gap-3">
        <div
          className="rounded-full flex items-center justify-center transition-transform duration-1000 ease-in-out"
          style={{
            width: 80,
            height: 80,
            background: 'linear-gradient(135deg, var(--soul-accent-light), var(--soul-accent))',
            transform: `scale(${scale})`,
            opacity: 0.8 + scale * 0.2,
          }}
        >
          <span className="text-white text-lg font-bold">{seconds}</span>
        </div>
        <p className="text-sm font-semibold" style={{ color: 'var(--soul-text)' }}>
          {current.label}
        </p>
        <div className="flex gap-1.5">
          {BREATHING_PHASES.map((_, i) => (
            <span
              key={i}
              className="w-2 h-2 rounded-full transition-colors"
              style={{ background: i === phase ? 'var(--soul-accent)' : 'var(--soul-border-light)' }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function GroundingWalkthrough({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState(0)
  const done = step >= GROUNDING_STEPS.length

  const handleNext = useCallback(() => {
    setStep((s) => s + 1)
  }, [])

  if (done) {
    return (
      <div className="mt-3 rounded-xl p-4 text-center" style={{ background: 'var(--soul-surface-alt)', border: '1px solid var(--soul-border-light)' }}>
        <p className="text-sm font-medium" style={{ color: 'var(--soul-text)' }}>
          You did it. Take a slow breath. You're here.
        </p>
        <button
          onClick={onClose}
          className="mt-3 text-xs px-3 py-1.5 rounded-full"
          style={{ color: 'white', background: 'var(--soul-accent)' }}
        >
          Done
        </button>
      </div>
    )
  }

  const current = GROUNDING_STEPS[step]

  return (
    <div className="mt-3 rounded-xl p-4" style={{ background: 'var(--soul-surface-alt)', border: '1px solid var(--soul-border-light)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium" style={{ color: 'var(--soul-text-muted)' }}>
          Step {step + 1} of {GROUNDING_STEPS.length}
        </span>
        <button
          onClick={onClose}
          className="text-xs px-2 py-0.5 rounded-full"
          style={{ color: 'var(--soul-text-muted)', background: 'var(--soul-surface)' }}
        >
          Close
        </button>
      </div>

      <div className="flex flex-col items-center gap-2">
        <span className="text-2xl font-bold" style={{ color: 'var(--soul-accent)' }}>
          {current.count}
        </span>
        <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--soul-text-muted)' }}>
          {current.sense}
        </p>
        <p className="text-sm text-center" style={{ color: 'var(--soul-text)' }}>
          {current.prompt}
        </p>
        <button
          onClick={handleNext}
          className="mt-2 text-xs px-4 py-1.5 rounded-full transition-colors"
          style={{ color: 'white', background: 'var(--soul-accent)' }}
        >
          {step < GROUNDING_STEPS.length - 1 ? 'Next' : 'Finish'}
        </button>
      </div>

      <div className="flex gap-1 justify-center mt-3">
        {GROUNDING_STEPS.map((_, i) => (
          <span
            key={i}
            className="w-2 h-2 rounded-full transition-colors"
            style={{ background: i <= step ? 'var(--soul-accent)' : 'var(--soul-border-light)' }}
          />
        ))}
      </div>
    </div>
  )
}

const CRISIS_EMOTIONS: Emotion[] = ['stressed', 'anxious', 'sad']

export function ResourcesCard({ emotion, aiSuggested }: Props) {
  const [activeTool, setActiveTool] = useState<ActiveTool>(null)
  const highlightCrisis = CRISIS_EMOTIONS.includes(emotion)

  return (
    <article
      className="dashboard-card dashboard-card-hover rounded-2xl border p-5"
      style={{ borderColor: 'var(--soul-border-light)' }}
    >
      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-lg section-heading" style={{ color: 'var(--soul-text)' }}>
          Resources
        </h3>
        {aiSuggested && (
          <span
            className="text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full"
            style={{ background: 'var(--soul-accent-pale)', color: 'var(--soul-accent)' }}
          >
            Suggested by AI
          </span>
        )}
      </div>

      {/* 988 Crisis Lifeline */}
      <div
        className="flex items-start gap-2.5 py-2 resource-row rounded-md px-2 -mx-1"
        style={{
          background: highlightCrisis ? 'var(--soul-accent-pale)' : 'transparent',
          border: highlightCrisis ? '1px solid var(--soul-accent-light)' : '1px solid transparent',
        }}
      >
        <span className="text-sm mt-0.5">{'\u260E'}</span>
        <div>
          <p className="text-sm font-medium" style={{ color: 'var(--soul-text)' }}>
            988 Suicide & Crisis Lifeline
          </p>
          <p className="text-xs" style={{ color: 'var(--soul-text-muted)' }}>
            <a href="tel:988" className="underline" style={{ color: 'var(--soul-accent)' }}>Call 988</a>
            {' or '}
            <a href="sms:988" className="underline" style={{ color: 'var(--soul-accent)' }}>Text 988</a>
            {' \u2014 available 24/7'}
          </p>
        </div>
      </div>

      {/* Box Breathing */}
      <div
        className="flex items-start gap-2.5 py-2 resource-row rounded-md px-2 -mx-1 cursor-pointer"
        style={{
          background: emotion === 'anxious' ? 'var(--soul-accent-pale)' : 'transparent',
          border: emotion === 'anxious' ? '1px solid var(--soul-accent-light)' : '1px solid transparent',
        }}
        onClick={() => setActiveTool(activeTool === 'breathing' ? null : 'breathing')}
      >
        <span className="text-sm mt-0.5">{'\uD83C\uDF2C\uFE0F'}</span>
        <div>
          <p className="text-sm font-medium" style={{ color: 'var(--soul-text)' }}>
            Box Breathing
          </p>
          <p className="text-xs" style={{ color: 'var(--soul-text-muted)' }}>
            {activeTool === 'breathing' ? 'Tap to close' : 'Tap to start guided breathing'}
          </p>
        </div>
      </div>
      {activeTool === 'breathing' && <BreathingGuide onClose={() => setActiveTool(null)} />}

      {/* 5-4-3-2-1 Grounding */}
      <div
        className="flex items-start gap-2.5 py-2 resource-row rounded-md px-2 -mx-1 cursor-pointer"
        style={{
          background: emotion === 'stressed' ? 'var(--soul-accent-pale)' : 'transparent',
          border: emotion === 'stressed' ? '1px solid var(--soul-accent-light)' : '1px solid transparent',
        }}
        onClick={() => setActiveTool(activeTool === 'grounding' ? null : 'grounding')}
      >
        <span className="text-sm mt-0.5">{'\uD83E\uDDD8'}</span>
        <div>
          <p className="text-sm font-medium" style={{ color: 'var(--soul-text)' }}>
            5-4-3-2-1 Grounding
          </p>
          <p className="text-xs" style={{ color: 'var(--soul-text-muted)' }}>
            {activeTool === 'grounding' ? 'Tap to close' : 'Tap for step-by-step walkthrough'}
          </p>
        </div>
      </div>
      {activeTool === 'grounding' && <GroundingWalkthrough onClose={() => setActiveTool(null)} />}
    </article>
  )
}
