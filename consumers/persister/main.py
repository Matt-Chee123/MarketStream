import os
import sys
from shared.kafka_client import KafkaConsumerWrapper
from batch_buffer import BatchBuffer
from datetime import datetime, timezone
import psycopg
import time


CREATE_TMP_SQL = """
    CREATE TEMP TABLE IF NOT EXISTS tmp_trades (
        LIKE trades INCLUDING DEFAULTS
    ) ON COMMIT DELETE ROWS
"""

COPY_SQL = """
    COPY tmp_trades (time, symbol, trade_id, price, quantity, is_buyer_maker)
    FROM STDIN
"""

MERGE_SQL = """
    INSERT INTO trades
    SELECT * FROM tmp_trades
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

def flush(cur, conn, consumer, rows):
    if not rows:
        return 0
    t0 = time.perf_counter()
    with cur.copy(COPY_SQL) as copy:
        for row in rows:
            copy.write_row(row)
    cur.execute(MERGE_SQL)
    conn.commit()
    consumer.commit()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return len(rows), elapsed_ms

def main():
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    DB_DSN = os.getenv("DB_DSN", "postgres://postgres:postgres@db:5432/mydb")

    conn = psycopg.connect(DB_DSN, autocommit=False)
    consumer = KafkaConsumerWrapper(
        broker=KAFKA_BROKER,
        topics="market.trades",
        group_id="persister"
    )
    buffer = BatchBuffer(1000, 1.0)

    with conn.cursor() as cur:
        cur.execute(CREATE_TMP_SQL)
        conn.commit()

    total = 0
    flush_count = 0
    last_report = time.perf_counter()
    report_interval = 5.0
    print("Listening for trades...")
    with conn.cursor() as cur:
        try:
            while True:
                for trade in consumer.poll():
                    buffer.add(parse_trade(trade))

                if buffer.should_flush():
                    trades = buffer.drain()
                    if trades:
                        n, elapsed_ms = flush(cur, conn, consumer, trades)
                        total += n
                        flush_count += 1

                    now = time.perf_counter()
                    if now - last_report >= report_interval:
                        rate = total / (now - last_report) if total > 0 else 0
                        avg_flush = (total / flush_count) if flush_count else 0
                        print(f"total={total}  rate={rate:,.0f}/s  flushes={flush_count}  "
                              f"avg_batch={avg_flush:.0f}  last_flush_ms={elapsed_ms:.1f}")
                        total = 0
                        flush_count = 0
                        last_report = now
        except Exception as e:
            print(f"Shutting down: {e}")


if __name__ == "__main__":
    main()