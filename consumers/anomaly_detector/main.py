import os
from shared.kafka_client import KafkaConsumerWrapper
from shared.kafka_producer import KafkaProducerWrapper
from shared.windows import SymbolFeatures

WINDOW_LENGTHS_MS = [300_000]   # 5-min window for the z-score
DETECTION_WINDOW_MS = 300_000
THRESHOLD = 3.5
MIN_SAMPLES = 30

INPUT_TOPIC = "market.trades"
OUTPUT_TOPIC = "market.anomalies"

def main():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    consumer = KafkaConsumerWrapper(
        broker=KAFKA_BROKER,
        topics=INPUT_TOPIC,
        group_id="anomaly-detector",
    )
    producer = KafkaProducerWrapper(KAFKA_BROKER)
    features = SymbolFeatures(WINDOW_LENGTHS_MS)

    print("Watching for anomalies")
    count = 0
    anomalies = 0
    try:
        for trade in consumer.messages():
            symbol = trade["symbol"]
            ts = trade["timestamp"]
            price = trade["price"]
            qty = trade["quantity"]
            window = features.symbols[symbol][DETECTION_WINDOW_MS]
            z = window.zscore(price, min_samples=MIN_SAMPLES)

            if z is not None and abs(z) > THRESHOLD:
                stats = window.stats()
                event = {
                    "symbol": symbol,
                    "timestamp": ts,
                    "price": price,
                    "zscore": z,
                    "window_mean": stats["mean_price"],
                    "window_std": stats["std_price"],
                    "window_count": stats["count"],
                }
                producer.send(OUTPUT_TOPIC, key=symbol, message=event)
                anomalies += 1
                print(f"ANOMALY {symbol} z={z:.2f} price={price:.4f}")

            features.update(symbol, ts, price, qty)

            count += 1
            if count % 1000 == 0:
                producer.flush()
                consumer.commit()
                print(f"Processed {count} trades, {anomalies} anomalies")

    except KeyboardInterrupt:
        print("Shutting down...")
        producer.flush()
        consumer.commit()
        producer.close()

if __name__ == "__main__":
    main()