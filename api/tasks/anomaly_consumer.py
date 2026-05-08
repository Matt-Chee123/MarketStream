from api.shared.kafka_consumer import KafkaConsumerWrapper
import asyncio
import os

async def anomaly_subscriber():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    KAFKA_TOPIC = os.getenv("ANOMALY_TOPIC", "market.trades")

    consumer = KafkaConsumerWrapper(KAFKA_BROKER, KAFKA_TOPIC, None)

    try:
        for anomaly in consumer.messages():
            print("xxxxxxxxxxxxxxxxxxx: ", anomaly)

    except KeyboardInterrupt:
        print("Shutting down...")
        consumer.commit()

if __name__ == "__main__":
    asyncio.run(anomaly_subscriber())