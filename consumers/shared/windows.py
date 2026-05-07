from collections import deque, defaultdict


class RollingWindow:
    def __init__(self, window_ms):
        self.window_ms = window_ms
        self.trades = deque()
        self.sum_p = 0.0
        self.sum_p2 = 0.0
        self.sum_notional = 0.0
        self.sum_qty = 0.0

    def add(self, timestamp_ms, price, quantity):
        self.trades.append((timestamp_ms, price, quantity))
        self.sum_p += price
        self.sum_p2 += price * price
        self.sum_notional += price * quantity
        self.sum_qty += quantity

        cutoff = timestamp_ms - self.window_ms
        while self.trades and self.trades[0][0] < cutoff:
            _, old_p, old_q = self.trades.popleft()
            self.sum_p -= old_p
            self.sum_p2 -= old_p * old_p
            self.sum_notional -= old_p * old_q
            self.sum_qty -= old_q

    def zscore(self, price, min_samples=30):
        s = self.stats()
        if s is None or s['count'] < min_samples or s['std_price'] == 0:
            return None
        return (price - s['mean_price']) / s['std_price']


    def stats(self):
        n = len(self.trades)
        if n == 0:
            return None
        mean = self.sum_p / n
        var = max(0.0, self.sum_p2 / n - mean * mean)
        return {
            "count": n,
            "mean_price": mean,
            "std_price": var ** 0.5,
            "vwap": self.sum_notional / self.sum_qty if self.sum_qty > 0 else mean,
            "last_price": self.trades[-1][1],
        }

    def stats_with_minmax(self):
        s = self.stats()
        if s is None:
            return None
        prices = [p for _, p, _ in self.trades]
        s["min_price"] = min(prices)
        s["max_price"] = max(prices)
        s["price_range"] = s["max_price"] - s["min_price"]
        return s


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
            stats = window.stats_with_minmax()
            if stats is None:
                continue
            out.append({
                "symbol": symbol,
                "window_end": timestamp_ms,
                "window_seconds": ms // 1000,
                **stats,
            })
        return out