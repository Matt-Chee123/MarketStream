from collections import deque, defaultdict


class RollingWindow:
    def __init__(self, window_ms):
        self.window_ms = window_ms
        self.trades = deque()

    def add(self, timestamp_ms, price, quantity):
        self.trades.append((timestamp_ms, price, quantity))
        cutoff = timestamp_ms - self.window_ms
        while self.trades and self.trades[0][0] < cutoff:
            self.trades.popleft()

    def zscore(self, price, min_samples=30):
        s = self.stats()
        if s is None or s['count'] < min_samples or s['std_price'] == 0:
            return None
        return (price - s['mean_price']) / s['std_price']


    def stats(self):
        if not self.trades:
            return None
        n = len(self.trades)
        prices = [p for _, p, _ in self.trades]
        quantities = [q for _, _, q in self.trades]
        notional = sum(q * p for q, p in zip(quantities, prices))
        total_qty = sum(quantities)
        mean = sum(prices) / n
        var = sum((p - mean) ** 2 for p in prices) / n
        return {
            "count": n,
            "mean_price": mean,
            "std_price": var ** 0.5,
            "vwap": notional / total_qty if total_qty > 0 else mean,
            "last_price": prices[-1],
            "min_price": min(prices),
            "max_price": max(prices),
        }

class SymbolFeatures:
    def __init__(self, window_ms):
        self.window_ms = window_ms
        self.symbols = defaultdict(lambda: {
            ms: RollingWindow(ms) for ms in window_ms
        })

    def update(self, symbol, timestamp_ms, price, quantity):
        for window in self.symbols[symbol].values():
            window.add(timestamp_ms, price, quantity)

    def snapshot(self, symbol, timestamp_ms):
        out = []
        for ms, window in self.symbols[symbol].items():
            stats = window.stats()
            if stats is None:
                continue
            out.append({
                "symbol": symbol,
                "window_end": timestamp_ms,
                "window_seconds": ms // 1000,
                **stats,
            })
        return out