import time
from core.ring_buffer import RingBuffer
import asyncio
import threading

class BaseStream:
    def __init__(self, ws_client, protocol, producer, monitor, topic, buffer=16384):
        self.ws_client = ws_client
        self.protocol = protocol
        self.producer = producer
        self.topic = topic
        self.monitor = monitor
        self.buffer = RingBuffer(buffer)
        self._stop = False

    async def _on_message(self, raw):

        t_received = time.time_ns()
        decoded = self.protocol.decode(raw)

        t_binance = decoded['timestamp']

        if not decoded:
            return

        payload = {
            'payload': decoded,
            't_received': t_received,
            't_binance': t_binance
        }

        while not self.buffer.push(payload):
            await asyncio.sleep(0.0001)

    def _reader_thread(self):
        async def run_ws():
            self.ws_client.on_message = self._on_message
            await self.ws_client.connect()
        asyncio.run(run_ws())

    def _publisher_thread(self):
        while not self._stop:
            payload = self.buffer.pop()
            if payload is None:
                time.sleep(0.0001)
                continue
            print(payload)
            self.producer.send(self.topic, payload['payload'])
            t_sent = time.time_ns()

            self.monitor.write_row(
                t_binance_ms=payload["t_binance"],
                t_received_ns=payload["t_received"],
                t_sent_ns=t_sent,
            )

    def run(self):
        reader = threading.Thread(target=self._reader_thread, name="reader", daemon=True)
        publisher = threading.Thread(target=self._publisher_thread, name="publisher", daemon=True)

        reader.start()
        publisher.start()

        try:
            reader.join()
        except KeyboardInterrupt:
            self._stop = True
            publisher.join(timeout=2.0)