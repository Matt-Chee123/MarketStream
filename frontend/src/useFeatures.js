import { useEffect, useState } from 'react'

export function useFeatures(symbol, { intervalMs = 1000 } = {}) {
  const [features, setFeatures] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!symbol) return

    let cancelled = false
    const ctrl = new AbortController()

    const fetchOnce = async () => {
      try {
        const res = await fetch(`/features/${symbol}`, { signal: ctrl.signal })
        if (cancelled) return
        if (!res.ok) {
          setError(`HTTP ${res.status}`)
          return
        }
        const data = await res.json()
        if (cancelled) return
        setFeatures(data)
        setError(null)
      } catch (e) {
        if (e.name === 'AbortError' || cancelled) return
        setError(e.message)
      }
    }

    fetchOnce()
    const id = setInterval(fetchOnce, intervalMs)

    return () => {
      cancelled = true
      ctrl.abort()
      clearInterval(id)
    }
  }, [symbol, intervalMs])

  return { features, error }
}