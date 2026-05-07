import os
import json
from fastapi import FastAPI, HTTPException
import redis.asyncio as redis_async

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
DEFAULT_VERSION = os.getenv("SCHEMA_VERSION", "v1")

app = FastAPI()
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