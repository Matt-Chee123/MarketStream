
class BaseStream:
    def __init__(self, ws_client, protocol, producer, topic):
        self.ws_client = ws_client
        self.protocol = protocol
        self.producer = producer
        self.topic = topic

    async def handle_message(self, raw):
        decoded = self.protocol.decode(raw)

        if decoded:
            self.producer.send(self.topic, decoded)

    async def run(self):
        self.ws_client.on_message = self.handle_message
        await self.ws_client.connect()