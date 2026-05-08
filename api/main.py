import os
import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import redis.asyncio as redis_async
from api.tasks.anomaly_consumer import  anomaly_subscriber
import asyncio
from contextlib import asynccontextmanager
from api.dashboard.connection_manager import manager
import asyncpg

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
DEFAULT_VERSION = os.getenv("SCHEMA_VERSION", "v1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[app] starting background tasks")
    DB_DSN = os.getenv("DB_DSN", "postgres://postgres:postgres@db:5432/mydb")
    app.state.pg = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=5)
    task = asyncio.create_task(anomaly_subscriber(manager), name="anomaly_subscriber")
    yield

    print("[app] stopping background tasks")
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    await app.state.pg.close()
    print("[app] shutdown complete")


app = FastAPI(lifespan=lifespan)
r = redis_async.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=1)

TRADES_SQL = """
WITH bucketed AS (
  SELECT
    time_bucket('1 second', time) AS bucket,
    last(price, time) AS price
  FROM trades
  WHERE symbol = $1
  GROUP BY bucket
  ORDER BY bucket DESC
  LIMIT $2
)
SELECT
  EXTRACT(EPOCH FROM bucket)::bigint AS time,
  price
FROM bucketed
ORDER BY time ASC
"""

@app.get("/trades/{symbol}")
async def get_trades(symbol: str, limit: int = 300):
    limit = max(1, min(limit, 2000))
    async with app.state.pg.acquire() as conn:
        rows = await conn.fetch(TRADES_SQL, symbol.upper(), limit)
    return [{"time": r["time"], "price": float(r["price"])} for r in rows]

@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "ok"}
    except redis_async.RedisError:
        raise HTTPException(503, "redis unavailable")

@app.get("/features/{symbol}")
async def get_features(symbol, window=60, version=DEFAULT_VERSION):
    key = f"feat:{symbol.upper()}:{window}s:{version}"
    raw = await r.get(key)
    if raw is None:
        raise HTTPException(404, f"no features for {symbol} window={window}s version={version}")
    return json.loads(raw)

@app.websocket("/stream")
async def stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)

