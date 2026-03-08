import json
import os

DB_FILE = "sales_db.json"

def _load() -> dict:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save(data: dict):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def read_db(key: str) -> str:
    return _load().get(key, "")

def update_db(key: str, value: str):
    data = _load()
    data[key] = value
    _save(data)
    print(f"DB updated: {key} → {value}")
