import { useEffect, useRef, useState } from 'react'

export function usePriceHistory(symbol, { intervalMs = 1000, maxPoints = 300 } = {}) {
  const [points, setPoints] = useState([])
  const lastTimeRef = useRef(0)

  useEffect(() => {
    if (!symbol) return
    let cancelled = false
    const ctrl = new AbortController()

    const seed = async () => {
      try {
        const res = await fetch(`/trades/${symbol}?limit=${maxPoints}`, { signal: ctrl.signal })
        if (cancelled || !res.ok) return
        const history = await res.json()
        const seeded = history.map((h) => ({ time: h.time, value: h.price }))
        setPoints(seeded)
        lastTimeRef.current = seeded.length ? seeded[seeded.length - 1].time : 0
      } catch (e) {
        if (e.name !== 'AbortError') console.error('seed failed', e)
      }
    }

    const tick = async () => {
      try {
        const res = await fetch(`/features/${symbol}`, { signal: ctrl.signal })
        if (cancelled || !res.ok) return
        const data = await res.json()

        const time = Math.floor(Number(data.window_end) / 1000)
        const value = Number(data.last_price)

        if (!Number.isFinite(time) || !Number.isFinite(value)) return
        if (time <= lastTimeRef.current) return

        lastTimeRef.current = time
        setPoints((prev) => {
          const next = [...prev, { time, value }]
          if (next.length > maxPoints) next.splice(0, next.length - maxPoints)
          return next
        })
      } catch (e) {
        if (e.name !== 'AbortError') console.error('tick failed', e)
      }
    }

    setPoints([])
    let intervalId = null
    seed().then(() => {
      if (!cancelled) intervalId = setInterval(tick, intervalMs)
    })

    return () => {
      cancelled = true
      ctrl.abort()
      if (intervalId) clearInterval(intervalId)
    }
  }, [symbol, intervalMs, maxPoints])

  return points
}