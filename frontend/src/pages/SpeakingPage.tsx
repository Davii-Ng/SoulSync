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
    <div className="flex flex-col gap-6" style={{ marginTop: '60px' }}>
      {/* Emotion signal */}
      <section className="flex items-center justify-center gap-3 py-2">
        <EmotionBadge emotion={emotion} />
      </section>

      {/* Voice orb */}
      <section className="flex flex-col items-center py-8 mb-4">
        <VoiceOrb state={orbState} onClick={onOrbClick} transcript={transcript} />
      </section>

      {/* Conversation card — chat + input together */}
      <section className="soul-card p-5 md:p-7 w-full flex flex-col">
        <ChatTranscript messages={messages} />
        <div className="mt-4">
          <TextInput onSend={onTextSend} disabled={isBusy} />
        </div>
      </section>

      {/* Bottom widgets */}
      <section className="pb-32 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <QuickCheckIn
            onCheckIn={(_mood, label) => {
              onTextSend(`I'm feeling ${label.toLowerCase()} right now`)
            }}
          />

          <article className="soul-card p-6">
            <h3 className="text-sm font-semibold tracking-wide uppercase mb-3" style={{ color: 'var(--soul-text-muted)' }}>
              Events
            </h3>
            {savedEvents.length === 0 ? (
              <p className="text-sm" style={{ color: 'var(--soul-text-muted)' }}>
                Mention a date or appointment and SoulSync will track it here.
              </p>
            ) : (
              <div className="rounded-2xl px-4 py-3" style={{ background: 'var(--soul-accent-pale)' }}>
                <p className="text-sm font-semibold" style={{ color: 'var(--soul-text)' }}>
                  {savedEvents[0]?.title}
                </p>
                <p className="text-xs mt-1" style={{ color: 'var(--soul-accent)' }}>
                  {savedEvents[0]?.dateLabel}
                </p>
                {savedEvents[0]?.note && (
                  <p className="text-xs mt-2" style={{ color: 'var(--soul-text-muted)' }}>
                    {savedEvents[0].note}
                  </p>
                )}
              </div>
            )}
          </article>
        </div>
      </section>
    </div>
  )
}
