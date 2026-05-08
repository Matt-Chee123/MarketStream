from api.shared.kafka_consumer import KafkaConsumerWrapper
import asyncio
import os

async def anomaly_subscriber(manager):
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    KAFKA_TOPIC = os.getenv("ANOMALY_TOPIC", "market.anomalies")

    consumer = KafkaConsumerWrapper(KAFKA_BROKER, KAFKA_TOPIC, None)
    loop = asyncio.get_running_loop()
    it = iter(consumer.messages())

    try:
        while True:
            anomaly = await loop.run_in_executor(None, next, it, None)
            if anomaly is None:
                break
            await manager.broadcast(anomaly)
    finally:
        try:
            consumer.commit()
        except Exception:
            pass