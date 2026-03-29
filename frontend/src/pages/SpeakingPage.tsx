import { VoiceOrb } from '../components/VoiceOrb'
import { ChatTranscript } from '../components/ChatTranscript'
import { TextInput } from '../components/TextInput'
import { EmotionBadge } from '../components/EmotionBadge'
import { ResourcesCard } from '../components/ResourcesCard'
import { QuickCheckIn } from '../components/QuickCheckIn'
import type { OrbState, Message, Emotion, SavedEvent } from '../types'

interface Props {
  orbState: OrbState
  messages: Message[]
  emotion: Emotion
  transcript: string
  isBusy: boolean
  savedEvents: SavedEvent[]
  onOrbClick: () => void
  onTextSend: (text: string) => void
}

export function SpeakingPage({
  orbState, messages, emotion, transcript, isBusy,
  savedEvents, onOrbClick, onTextSend,
}: Props) {
  return (
    <div className="flex flex-col gap-5">
      {/* Emotion strip */}
      <section
        className="dashboard-strip rounded-2xl border px-5 py-3.5 flex items-center justify-center gap-4"
        style={{ borderColor: 'var(--soul-border-light)' }}
      >
        <span className="text-sm" style={{ color: 'var(--soul-text-secondary)' }}>
          Emotion signal:
        </span>
        <EmotionBadge emotion={emotion} />
        <span className="text-sm hidden sm:inline" style={{ color: 'var(--soul-text-muted)' }}>
          tone adapts with mood in real time
        </span>
      </section>

      {/* Voice orb */}
      <section className="flex flex-col items-center py-4 md:py-6">
        <VoiceOrb state={orbState} onClick={onOrbClick} transcript={transcript} />
      </section>

      {/* Chat section */}
      <section
        className="dashboard-chat rounded-2xl border p-4 md:p-5"
        style={{ borderColor: 'var(--soul-border-light)' }}
      >
        <ChatTranscript messages={messages} />
        <div className="mt-5">
          <TextInput onSend={onTextSend} disabled={isBusy} />
        </div>
      </section>

      {/* Dashboard cards: Quick Check-in, Events, Resources */}
      <section className="pt-1 md:pt-0">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
          <QuickCheckIn
            onCheckIn={(_mood, label) => {
              onTextSend(`I'm feeling ${label.toLowerCase()} right now`)
            }}
          />

          <article
            className="dashboard-card dashboard-card-hover rounded-2xl border p-5"
            style={{ borderColor: 'var(--soul-border-light)' }}
          >
            <h3 className="text-lg section-heading" style={{ color: 'var(--soul-text)' }}>
              Events
            </h3>
            {savedEvents.length === 0 ? (
              <p className="text-xs mt-3" style={{ color: 'var(--soul-text-muted)' }}>
                Mention a date or appointment and SoulSync will track it here.
              </p>
            ) : (
              <>
                <div
                  className="mt-3 rounded-lg px-3.5 py-2.5"
                  style={{
                    background: 'var(--soul-accent-pale)',
                    border: '1px solid var(--soul-accent-light)',
                  }}
                >
                  <p className="text-sm font-medium" style={{ color: 'var(--soul-text)' }}>
                    {savedEvents[0]?.title}
                  </p>
                  <p className="text-xs mt-1" style={{ color: 'var(--soul-accent)' }}>
                    {savedEvents[0]?.dateLabel}
                  </p>
                </div>
                <p className="text-xs mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                  {savedEvents[0]?.note}
                </p>
              </>
            )}
          </article>

          <ResourcesCard
            emotion={emotion}
            aiSuggested={['stressed', 'anxious', 'sad', 'angry'].includes(emotion)}
          />
        </div>
      </section>
    </div>
  )
}
