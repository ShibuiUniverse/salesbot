import os
import sys

REQUIRED = [
    "OPENSEA_API_KEY",
    "TWITTER_CONSUMER_KEY",
    "TWITTER_CONSUMER_SECRET",
    "TWITTER_BEARER_TOKEN",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET",
    "DISCORD_WEBHOOK_URL",
    "CF_IMAGE_BASE",
    "REDIS_URL",
]

def _load():
    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        print(f"[FATAL] Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    return {k: os.environ[k] for k in REQUIRED}

cfg = _load()
