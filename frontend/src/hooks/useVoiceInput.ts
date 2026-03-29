// Web Speech API hook for voice-to-text

import { useState, useRef, useCallback } from 'react'

interface UseVoiceInputReturn {
  isListening: boolean
  transcript: string
  startListening: (onResult: (text: string) => void) => void
  stopListening: () => void
}

export function useVoiceInput(): UseVoiceInputReturn {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const callbackRef = useRef<((text: string) => void) | null>(null)
  const latestTranscriptRef = useRef('')

  const startListening = useCallback((onResult: (text: string) => void) => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.error('Speech Recognition not supported')
      return
    }

    callbackRef.current = onResult
    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.interimResults = false
    recognition.continuous = false

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript
      latestTranscriptRef.current = text
      setTranscript(text)
    }

    // Fire callback with final transcript when recognition fully stops
    recognition.onend = () => {
      setIsListening(false)
      if (callbackRef.current && latestTranscriptRef.current) {
        callbackRef.current(latestTranscriptRef.current)
      }
      callbackRef.current = null
    }

    recognition.onerror = () => {
      setIsListening(false)
      callbackRef.current = null
    }

    recognitionRef.current = recognition
    latestTranscriptRef.current = ''
    setTranscript('')
    recognition.start()
    setIsListening(true)
  }, [])

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop()
  }, [])

  return { isListening, transcript, startListening, stopListening }
}
