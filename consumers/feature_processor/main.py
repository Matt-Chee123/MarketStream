import os
from shared.kafka_producer import KafkaProducerWrapper
from shared.windows import SymbolFeatures
from shared.kafka_client import KafkaConsumerWrapper


WINDOW_LENGTHS_MS = [60_000, 300_000]
INPUT_TOPIC = "market.trades"
OUTPUT_TOPIC = "market.features"


def main():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

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
                print(record)
                producer.send(OUTPUT_TOPIC, key=record["symbol"], message=record)

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


if __name__ == "__main__":
    main()