import time

class BaseStream:
    def __init__(self, ws_client, protocol, producer, monitor, topic):
        self.ws_client = ws_client
        self.protocol = protocol
        self.producer = producer
        self.topic = topic
        self.monitor = monitor

    async def handle_message(self, raw):

        t_received = time.time_ns()
        decoded = self.protocol.decode(raw)

        t_binance = decoded['timestamp']

        if not decoded:
            return

        self.producer.send(self.topic, decoded)
        t_sent = time.time_ns()

        self.monitor.write_row(t_binance, t_received, t_sent)

    async def run(self):
        self.ws_client.on_message = self.handle_message
        await self.ws_client.connect()