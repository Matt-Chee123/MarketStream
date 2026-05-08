function severity(z) {
  const a = Math.abs(z)
  if (a >= 8) return 'extreme'
  if (a >= 5) return 'high'
  if (a >= 3) return 'med'
  return 'low'
}

function fmtTime(ts) {
  const d = new Date(ts)
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}:${String(d.getSeconds()).padStart(2,'0')}`
}

export default function AnomalyLog({ messages }) {
  if (messages.length === 0) {
    return (
      <div className="log__empty">
        <div className="log__empty-line">awaiting anomalies</div>
      </div>
    )
  }

  return (
    <ul className="log">
      {messages.map((m, i) => (
        <li key={i} className={`log__row log__row--${severity(m.zscore)}`}>
          <span className="log__time">{fmtTime(m.timestamp)}</span>
          <span className="log__symbol">{m.symbol}</span>
          <span className="log__z">
            {m.zscore < 0 ? '▼' : '▲'} {m.zscore.toFixed(2)}
          </span>
        </li>
      ))}
    </ul>
  )
}