import asyncio
from streams.trades import create_trade_stream

if __name__ == "__main__":
    stream = create_trade_stream()
    stream.run()