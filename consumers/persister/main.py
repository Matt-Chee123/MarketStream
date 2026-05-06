import os
import sys
from shared.kafka_client import KafkaConsumerWrapper

def main():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    consumer = KafkaConsumerWrapper(
        broker=KAFKA_BROKER,
        topics="market.trades",
        group_id="persister"
    )
    print("Listening for trades...")
    count = 0
    for trade in consumer.messages():
        print(trade)
        count += 1
        if count % 100 == 0:
            print(f"Received {count} trades, latest: {trade}")


if __name__ == "__main__":
    main()