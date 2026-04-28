from core.websocket_client import WebsocketClient
from core.kafka_producer import KafkaProducerWrapper
from core.base_stream import BaseStream
from protocols.binance_protocol import BinanceProtocol
import os

def create_trade_stream():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    url = (
        "wss://stream.binance.com:9443/stream"
        "?streams=btcusdt@trade/ethusdt@trade"
    )
    ws = WebsocketClient(url, on_message=None)
    protocol = BinanceProtocol()
    producer = KafkaProducerWrapper(KAFKA_BROKER)

    return BaseStream(ws, protocol, producer, topic="market.trades")