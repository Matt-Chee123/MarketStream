import os
import sys
from shared.kafka_client import KafkaConsumerWrapper
from datetime import datetime, timezone
import psycopg


INSERT_SQL = """
    INSERT INTO trades (time, symbol, trade_id, price, quantity, is_buyer_maker)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING
"""

def parse_trade(msg):
    return (
        datetime.fromtimestamp(msg["timestamp"] / 1000, tz=timezone.utc),
        msg["symbol"],
        msg["trade_id"],
        msg["price"],
        msg["quantity"],
        msg["is_buyer_maker"],
    )

def main():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    DB_DSN = os.getenv("DB_DSN", "postgres://postgres:postgres@db:5432/mydb")

    conn = psycopg.connect(DB_DSN, autocommit=False)
    consumer = KafkaConsumerWrapper(
        broker=KAFKA_BROKER,
        topics="market.trades",
        group_id="persister"
    )
    print("Listening for trades...")
    with conn.cursor() as cur:
        for trade in consumer.messages():
            cur.execute(INSERT_SQL, parse_trade(trade))
            conn.commit()
            consumer.commit()
            print(trade)


if __name__ == "__main__":
    main()