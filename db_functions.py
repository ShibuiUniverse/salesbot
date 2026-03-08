import redis
from config import cfg

_client = redis.from_url(cfg["REDIS_URL"], decode_responses=True)

def read_db(key: str) -> str:
    return _client.get(key) or ""

def update_db(key: str, value: str):
    _client.set(key, value)
    print(f"DB updated: {key} → {value}")
