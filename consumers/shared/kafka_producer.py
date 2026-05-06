from kafka import KafkaProducer
import orjson
import time

class KafkaProducerWrapper:
    def __init__(self, broker):
        while True:
            try:
                print(f"Connecting to Kafka at {broker}...")
                self.producer = KafkaProducer(
                    bootstrap_servers=broker,
                    value_serializer=lambda v: orjson.dumps(v),
                    api_version_auto_timeout_ms=5000
                )
                print("✅ Connected to Kafka")
                break
            except Exception as e:
                print(f"❌ Kafka not ready: {e}")
                time.sleep(5)

    def send(self, topic, key, message):
        self.producer.send(topic, key=key.encode() if isinstance(key, str) else key, value=message)