import os
from shared.kafka_producer import KafkaProducerWrapper
from shared.windows import SymbolFeatures
from shared.kafka_client import KafkaConsumerWrapper
import redis
import json
from collections import defaultdict

WINDOW_LENGTHS_MS = [60_000, 300_000]
INPUT_TOPIC = "market.trades"
OUTPUT_TOPIC = "market.features"
SCHEMA_VERSION = "v1"
SNAPSHOT_INTERVAL_MS = 1000

def main():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    consumer = KafkaConsumerWrapper(
        broker=KAFKA_BROKER,
        topics=INPUT_TOPIC,
        group_id="feature-processor",
    )
    producer = KafkaProducerWrapper(broker=KAFKA_BROKER)
    features = SymbolFeatures(WINDOW_LENGTHS_MS)
    last_bucket = defaultdict(lambda: 0)

    print("Computing features...")
    count = 0
    try:
        for trade in consumer.messages():
            features.update(
                trade["symbol"],
                trade["timestamp"],
                trade["price"],
                trade["quantity"],
            )

            bucket = (trade["timestamp"] // SNAPSHOT_INTERVAL_MS) * SNAPSHOT_INTERVAL_MS
            if bucket > last_bucket[trade["symbol"]]:
                last_bucket[trade["symbol"]] = bucket

                for record in features.snapshot(trade["symbol"], bucket):
                    kafka_key = f"{trade["symbol"]}:{record['window_seconds']}:{bucket}"
                    producer.send(OUTPUT_TOPIC, key=kafka_key, message=record)

                    redis_key = f"feat:{trade["symbol"]}:{record['window_seconds']}s:{SCHEMA_VERSION}"
                    r.set(redis_key, json.dumps(record, default=str))

            count += 1
            if count % 1000 == 0:
                producer.flush()
                consumer.commit()
                print(f"Processed {count} trades")


    except KeyboardInterrupt:
        print("Shutting down...")
        producer.flush()
        consumer.commit()
        producer.close()
        r.close()

if __name__ == "__main__":
    main()