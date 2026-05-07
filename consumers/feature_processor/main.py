import os
from shared.kafka_producer import KafkaProducerWrapper
from shared.windows import SymbolFeatures
from shared.kafka_client import KafkaConsumerWrapper
import redis
import json

WINDOW_LENGTHS_MS = [60_000, 300_000]
INPUT_TOPIC = "market.trades"
OUTPUT_TOPIC = "market.features"
SCHEMA_VERSION = "v1"


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
            for record in features.snapshot(trade["symbol"], trade["timestamp"]):
                producer.send(OUTPUT_TOPIC, key=record["symbol"], message=record)
                key = f"feat:{record['symbol']}:{record['window_seconds']}s:{SCHEMA_VERSION}"
                print(key)
                r.set(key, json.dumps(record, default=str))

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