import os
import json
from fastapi import FastAPI, HTTPException
import redis.asyncio as redis_async
from api.tasks.anomaly_consumer import  anomaly_subscriber
import asyncio
from contextlib import asynccontextmanager

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
DEFAULT_VERSION = os.getenv("SCHEMA_VERSION", "v1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[app] starting background tasks")
    task = asyncio.create_task(anomaly_subscriber(), name="anomaly_subscriber")

    yield

    print("[app] stopping background tasks")
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    print("[app] shutdown complete")

app = FastAPI(lifespan=lifespan)
r = redis_async.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=1)


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