import { useState } from 'react'
import { useAnomalyStream } from './useAnomalyStream'
import { useFeatures } from './useFeatures'
import { usePriceHistory } from './usePriceHistory'
import PriceChart from './components/PriceChart'
import AnomalyLog from './components/AnomalyLog'

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

export default function App() {
  const [symbol, setSymbol] = useState(SYMBOLS[0])

  const { messages, status } = useAnomalyStream('ws://localhost:8000/stream')
  const { features } = useFeatures(symbol)
  const points = usePriceHistory(symbol)

  return (
    <div className="app">
      <header className="header">
        <div className="header__left">
          <h1 className="brand">
            Market<span className="brand__italic">stream</span>
          </h1>
          <select
            className="symbol-select"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
          >
            {SYMBOLS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className={`status status--${status}`}>
          <span className="status__dot" />
          <span className="status__label">{status === 'connected' ? 'LIVE' : status.toUpperCase()}</span>
        </div>
      </header>

      <section className="stats">
        <Stat label="last price" value={features ? features.last_price.toLocaleString('en-US', { maximumFractionDigits: 2 }) : '—'} />
        <Stat label="μ window"   value={features ? features.mean_price.toFixed(2) : '—'} />
        <Stat label="σ window"   value={features ? features.std_price.toFixed(2) : '—'} />
        <Stat label="n trades"   value={features ? features.count.toLocaleString('en-US') : '—'} />
      </section>

      <main className="grid">
        <div className="panel panel--chart">
          <PriceChart points={points} />
        </div>
        <div className="panel panel--log">
          <div className="panel__header">anomalies</div>
            <AnomalyLog messages={messages.slice(0, 20)} />
        </div>
      </main>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <div className="stat__label">{label}</div>
      <div className="stat__value">{value}</div>
    </div>
  )
}