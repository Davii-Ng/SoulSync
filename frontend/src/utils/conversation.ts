import type { SavedEvent } from '../types'

export const getEventId = (event: SavedEvent): string => {
  const trimmed = event.id?.trim()
  if (trimmed) return trimmed
  return `${event.title}|${event.dateLabel}`.toLowerCase()
}

export const mergeEvents = (existing: SavedEvent[], incoming: SavedEvent[]): SavedEvent[] => {
  if (incoming.length === 0) return existing
  const byId = new Map<string, SavedEvent>()
  for (const event of existing) {
    byId.set(getEventId(event), { ...event, id: getEventId(event) })
  }
  for (const event of incoming) {
    const normalized = { ...event, id: getEventId(event) }
    byId.set(normalized.id, normalized)
  }
  return Array.from(byId.values())
}

// Phrases that signal the user wants to save today's journal
const SAVE_PHRASES = [
  'save today', 'save journal', 'save this conversation', 'save my journal',
  "that's it for today", 'thats it for today', 'done for the day', 'done for today',
  'wrap up', 'end session', 'save the chat', 'save chat',
]

export function isSaveIntent(text: string): boolean {
  const lower = text.toLowerCase()
  return SAVE_PHRASES.some((p) => lower.includes(p))
}
