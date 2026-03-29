import { VoiceOrb } from '../components/VoiceOrb'
import { ChatTranscript } from '../components/ChatTranscript'
import { TextInput } from '../components/TextInput'
import { EmotionBadge } from '../components/EmotionBadge'
import type { OrbState, Message, Emotion } from '../types'

interface Props {
  orbState: OrbState
  messages: Message[]
  emotion: Emotion
  transcript: string
  isBusy: boolean
  onOrbClick: () => void
  onTextSend: (text: string) => void
}

export function SpeakingPage({ orbState, messages, emotion, transcript, isBusy, onOrbClick, onTextSend }: Props) {
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
    </div>
  )
}
