from kafka import KafkaConsumer
import orjson
import time

class KafkaConsumerWrapper:
    def __init__(self, broker, topics, group_id, auto_offset_reset="latest"):
        while True:
            try:
                print(f"Connecting to Kafka at {broker}...")
                self.consumer = KafkaConsumer(
                    topics,
                    bootstrap_servers=broker,
                    group_id=group_id,
                    enable_auto_commit=False,
                    auto_offset_reset=auto_offset_reset,
                    value_deserializer=orjson.loads,
                )
                break
            except Exception as e:
                print(f"❌ Kafka not ready: {e}")
                time.sleep(5)

    def messages(self):
        for msg in self.consumer:
            yield msg.value

    def commit(self):
        self.consumer.commit()

    def close(self):
        self.consumer.close()

    def poll(self, timeout_ms=200):
        records = self.consumer.poll(timeout_ms=timeout_ms)
        out = []
        for tp_record in records.values():
            print("xxxxxxxxxxxxxxxxxxxxxxxxx")
            print(tp_record)
            for record in tp_record:
                print("xxxxxxxxxxxxxxxxx")
                print(record)
                out.append(record.value)
        return out
