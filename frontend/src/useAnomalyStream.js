import { useEffect, useState } from 'react'

export function useAnomalyStream(url) {
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState('connecting')

  useEffect(() => {
    const ws = new WebSocket(url)

    ws.onopen = () => setStatus('connected')
    ws.onclose = () => setStatus('disconnected')
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      setMessages((prev) => [msg, ...prev].slice(0, 50))
    }

    return () => ws.close()
  }, [url])

  return { messages, status }
}