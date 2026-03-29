import { VoiceOrb } from '../components/VoiceOrb'
import { ChatTranscript } from '../components/ChatTranscript'
import { TextInput } from '../components/TextInput'
import { EmotionBadge } from '../components/EmotionBadge'
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
      <section className="dashboard-strip px-5 py-3.5 flex items-center justify-center gap-4">
        <span className="tech-font text-[var(--soul-accent-light)]">
          // SIGNAL_STATUS:
        </span>
        <EmotionBadge emotion={emotion} />
        <span className="text-xs hidden sm:inline tech-font opacity-70">
          [ ADAPTIVE_TONE_ACTIVE ]
        </span>
      </section>

      {/* Voice orb */}
      <section className="flex flex-col items-center pb-6 w-full" style={{ paddingTop: '15vh' }}>
        <VoiceOrb state={orbState} onClick={onOrbClick} transcript={transcript} />
      </section>

      {/* Chat section */}
      <section className="dashboard-chat w-full pt-4">
        <div className="dashboard-card p-4 md:p-6 w-full flex flex-col">
          <ChatTranscript messages={messages} />
          <div className="mt-4 pt-4 border-t border-[var(--soul-border-light)]">
            <TextInput onSend={onTextSend} disabled={isBusy} />
          </div>
        </div>
      </section>

      {/* Dashboard cards: Quick Check-in, Events */}
      <section className="pt-8 pb-[180px] w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 md:gap-6">
          <QuickCheckIn
            onCheckIn={(_mood, label) => {
              onTextSend(`I'm feeling ${label.toLowerCase()} right now`)
            }}
          />

          <article className="dashboard-card dashboard-card-hover p-7 flex flex-col justify-between">
            <div>
              <h3 className="tech-font text-[var(--soul-accent-light)] mb-2">
                &gt; SYSTEM_EVENTS
              </h3>
              {savedEvents.length === 0 ? (
                <p className="text-sm mt-3 opacity-60">
                  <span className="tech-font">null</span> {/* No active events logged. */} 
                  <br/><br/> Mention a date or appointment and SoulSync will track it here.
                </p>
              ) : (
                <>
                  <div className="mt-4 rounded-xl px-4 py-3 bg-[var(--soul-surface-alt)] border border-[var(--soul-border)]">
                    <p className="font-semibold text-lg text-[var(--soul-text)]">
                      {savedEvents[0]?.title}
                    </p>
                    <p className="text-sm mt-1 font-mono text-[var(--soul-accent)]">
                      {savedEvents[0]?.dateLabel}
                    </p>
                  </div>
                  <p className="text-xs mt-3 opacity-75">
                    {savedEvents[0]?.note}
                  </p>
                </>
              )}
            </div>
          </article>
        </div>
      </section>
    </div>
  )
}
