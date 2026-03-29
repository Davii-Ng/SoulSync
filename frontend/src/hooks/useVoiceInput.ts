// Web Speech API hook for voice-to-text

import { useState, useRef, useCallback } from 'react'

interface UseVoiceInputReturn {
  isListening: boolean
  transcript: string
  startListening: () => void
  stopListening: () => Promise<string>
}

export function useVoiceInput(): UseVoiceInputReturn {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const latestTranscriptRef = useRef('')

  const startListening = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.error('Speech Recognition not supported')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.interimResults = true
    recognition.continuous = true

    recognition.onresult = (event) => {
      // Concat all results (continuous mode produces multiple)
      let text = ''
      for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript
      }
      latestTranscriptRef.current = text
      setTranscript(text)
    }

    recognition.onend = () => setIsListening(false)
    recognition.onerror = () => {
      console.error('Speech recognition error')
      setIsListening(false)
    }

    recognitionRef.current = recognition
    latestTranscriptRef.current = ''
    setTranscript('')
    recognition.start()
    setIsListening(true)
  }, [])

  const stopListening = useCallback((): Promise<string> => {
    return new Promise((resolve) => {
      const recognition = recognitionRef.current
      if (!recognition) {
        setIsListening(false)
        resolve('')
        return
      }

      // Override onend to resolve after final onresult has fired
      recognition.onend = () => {
        setIsListening(false)
        resolve(latestTranscriptRef.current)
      }

      recognition.stop()
    })
  }, [])

  return { isListening, transcript, startListening, stopListening }
}