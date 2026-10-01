import { describe, expect, it } from 'vitest'
import { getEventId, isSaveIntent, mergeEvents } from './conversation'
import type { SavedEvent } from '../types'

const event = (over: Partial<SavedEvent> = {}): SavedEvent => ({
  id: '',
  title: 'Dentist',
  dateLabel: '2026-05-22 15:00',
  ...over,
})

describe('getEventId', () => {
  it('keeps a provided id, trimmed', () => {
    expect(getEventId(event({ id: '  abc  ' }))).toBe('abc')
  })

  it('derives a lowercase id from title and date when id is blank', () => {
    expect(getEventId(event())).toBe('dentist|2026-05-22 15:00')
  })
})

describe('mergeEvents', () => {
  it('returns the same array when nothing is incoming', () => {
    const existing = [event()]
    expect(mergeEvents(existing, [])).toBe(existing)
  })

  it('dedupes by id and lets the newer event win', () => {
    const merged = mergeEvents([event({ note: 'old' })], [event({ note: 'new' })])
    expect(merged).toHaveLength(1)
    expect(merged[0].note).toBe('new')
  })

  it('keeps distinct events', () => {
    const merged = mergeEvents([event()], [event({ title: 'Interview' })])
    expect(merged.map((e) => e.title)).toEqual(['Dentist', 'Interview'])
  })
})

describe('isSaveIntent', () => {
  it.each([
    'Save today please',
    "That's it for today",
    'I am DONE FOR THE DAY',
    'wrap up',
    'save my journal',
  ])('detects %j', (text) => {
    expect(isSaveIntent(text)).toBe(true)
  })

  it.each(['I feel stressed', 'what should I save for retirement', ''])('ignores %j', (text) => {
    expect(isSaveIntent(text)).toBe(false)
  })
})
