// Manages WebSocket connection to backend

import { useEffect, useRef, useCallback, useState } from 'react'
import { WS_URL } from '../utils/constants'
import type { Message, Emotion } from '../types'

interface WSMessage {
  type: 'response' | 'emotion' | 'error'
  content?: string
  emotion?: Emotion
  audio_url?: string
}

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const socket = new WebSocket(WS_URL)

    socket.onopen = () => setIsConnected(true)
    socket.onclose = () => setIsConnected(false)
    socket.onerror = () => setIsConnected(false)

    ws.current = socket

    return () => {
      socket.close()
    }
  }, [])

  const sendMessage = useCallback((text: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'text', content: text }))
    }
  }, [])

  return { isConnected, sendMessage, ws }
}