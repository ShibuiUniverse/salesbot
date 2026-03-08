import time
import requests
from tweet import send_tweet
from db_functions import update_db, read_db
import os

CONTRACT        = "0xd592924c2abcc1b532114917e697609cb415589c"
COLLECTION      = "Pirates of Fukushū"
OPENSEA_SLUG    = "pirates-of-fukushu"
OPENSEA_API_KEY = os.environ["OPENSEA_API_KEY"]
POLL_INTERVAL   = 120
DB_KEY          = "pirates_eth"

def get_eth_price_usd():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ethereum", "vs_currencies": "usd"},
            timeout=10,
        )
        return float(r.json()["ethereum"]["usd"])
    except Exception as e:
        print(f"Could not fetch ETH price: {e}")
        return 0.0

def get_recent_sales():
    url = f"https://api.opensea.io/api/v2/events/collection/{OPENSEA_SLUG}"
    headers = {
        "accept": "application/json",
        "x-api-key": OPENSEA_API_KEY,
    }
    params = {"event_type": "sale", "limit": 50}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("asset_events", [])
    except Exception as e:
        print(f"OpenSea API error: {e}")
        return []

def parse_event(event):
    try:
        tx_hash  = event.get("transaction", "")
        token_id = event["nft"]["identifier"]
        payment  = event.get("payment", {})
        decimals = int(payment.get("decimals", 18))
        quantity = int(payment.get("quantity", 0))
        eth_price = quantity / (10 ** decimals)
        if eth_price == 0:
            return None
        return {"tx_hash": tx_hash, "token_id": token_id, "eth": eth_price}
    except Exception as e:
        print(f"Could not parse event: {e}")
        return None

def track():
    print(f"[Shibui Sales Bot] Checking {COLLECTION} sales on ETH...")
    last_tx   = read_db(DB_KEY)
    events    = get_recent_sales()
    eth_price = get_eth_price_usd()
    new_sales = []
    for event in events:
        tx = event.get("transaction", "")
        if tx == last_tx:
            break
        parsed = parse_event(event)
        if parsed:
            new_sales.append(parsed)
    new_sales.reverse()
    for sale in new_sales:
        usd = sale["eth"] * eth_price
        print(f"  → Sale: #{sale['token_id']}  {sale['eth']:.4f} ETH  (${usd:.2f})")
        update_db(DB_KEY, sale["tx_hash"])
        time.sleep(1)
        send_tweet(sale, COLLECTION, CONTRACT, eth_price)
    if not new_sales:
        print("  No new sales.")

print("Shibui ETH Sales Bot starting...")
while True:
    try:
        track()
    except Exception as e:
        print(f"Unexpected error: {e}")
    time.sleep(POLL_INTERVAL)
