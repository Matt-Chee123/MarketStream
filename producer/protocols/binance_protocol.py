import orjson
from .base_protocol import BaseProtocol

class BinanceProtocol(BaseProtocol):
    def decode(self, raw):
        msg = orjson.loads(raw)

        if "data" not in msg:
            return None

        data = msg["data"]

        if data.get("e") != "trade":
            return None

        return {
            "symbol": data["s"],
            "price": float(data["p"]),
            "quantity": float(data["q"]),
            "timestamp": data["E"],
        }