// Manages WebSocket connection to backend with auto-reconnect

import { useEffect, useRef, useCallback, useState } from 'react'
import { WS_URL } from '../utils/constants'

const MAX_RETRIES = 3
const BASE_DELAY_MS = 1000

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const retryCount = useRef(0)
  const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const disposed = useRef(false)

  const connect = useCallback(() => {
    if (disposed.current) return

    const socket = new WebSocket(WS_URL)

    socket.onopen = () => {
      if (disposed.current) { socket.close(); return }
      setIsConnected(true)
      retryCount.current = 0
    }

    socket.onclose = () => {
      setIsConnected(false)
      ws.current = null
      // Auto-reconnect with exponential backoff (skip if unmounted)
      if (!disposed.current && retryCount.current < MAX_RETRIES) {
        const delay = BASE_DELAY_MS * 2 ** retryCount.current
        retryCount.current += 1
        retryTimer.current = setTimeout(connect, delay)
      }
    }

    socket.onerror = () => {
      setIsConnected(false)
    }

    ws.current = socket
  }, [])

  useEffect(() => {
    disposed.current = false
    connect()

    return () => {
      disposed.current = true
      if (retryTimer.current) clearTimeout(retryTimer.current)
      // Only close if already open — avoids the "closed before established" warning
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.close()
      }
    }
  }, [connect])

  const sendMessage = useCallback((text: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'text', content: text }))
    }
  }, [])

  return { isConnected, sendMessage, ws }
}
