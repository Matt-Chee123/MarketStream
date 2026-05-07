import os
import time
import random
import itertools
from shared.kafka_producer import KafkaProducerWrapper

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TARGET_RATE = int(os.getenv("TARGET_RATE", "30000"))
DURATION_S  = int(os.getenv("DURATION_S", "60"))
TOPIC       = os.getenv("TOPIC", "market.trades")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
BASE_PRICES = {
    "BTCUSDT": 80_000.0,
    "ETHUSDT":  3_000.0,
    "SOLUSDT":    150.0,
    "XRPUSDT":      0.6,
    "ADAUSDT":      0.4,
}
BATCH_SIZE = max(1, TARGET_RATE // 500)

def make_trade(trade_id):
    symbol = random.choice(SYMBOLS)
    price = BASE_PRICES[symbol]
    return {
        "symbol": symbol,
        "trade_id": trade_id,
        "price": round(price * random.uniform(0.995, 1.005), 4),
        "quantity": round(random.uniform(0.001, 5), 4),
        "timestamp": int(time.time() * 1000),
        "is_buyer_maker": random.choice([True, False]),
    }

def main():
    producer = KafkaProducerWrapper(broker=KAFKA_BROKER)
    print(f"Synthetic producer: target {TARGET_RATE} msgs/sec, "
          f"batch size {BATCH_SIZE}, duration {DURATION_S or '∞'}s")

    start = time.perf_counter()
    batch_interval = BATCH_SIZE / TARGET_RATE
    next_batch = start
    sent = 0
    last_report = start
    counter = itertools.count(1)

    try:
        while True:
            now = time.perf_counter()

            for _ in range(BATCH_SIZE):
                trade_id = next(counter)
                trade = make_trade(trade_id)
                producer.send(TOPIC, key=trade["symbol"], message=trade)
                sent += 1

            next_batch += batch_interval
            sleep_for = next_batch - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)

            if now - last_report >= 5:
                elapsed = now - start
                actual_rate = sent / elapsed
                print(f"sent={sent:>8d}  elapsed={elapsed:>5.1f}s  "
                      f"rate={actual_rate:>8,.0f}/s  target={TARGET_RATE:,}/s")
                last_report = now

            if DURATION_S and now - start >= DURATION_S:
                break

    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        producer.flush()
        producer.close()
        elapsed = time.perf_counter() - start
        print(f"Final: sent={sent} in {elapsed:.1f}s = {sent/elapsed:,.0f}/s")


if __name__ == "__main__":
    main()