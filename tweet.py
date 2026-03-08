import os
import tweepy
import requests
from config import cfg

consumer_key        = cfg["TWITTER_CONSUMER_KEY"]
consumer_secret     = cfg["TWITTER_CONSUMER_SECRET"]
bearer_token        = cfg["TWITTER_BEARER_TOKEN"]
access_token        = cfg["TWITTER_ACCESS_TOKEN"]
access_token_secret = cfg["TWITTER_ACCESS_TOKEN_SECRET"]
DISCORD_WEBHOOK     = cfg["DISCORD_WEBHOOK_URL"]
CF_IMAGE_BASE       = cfg["CF_IMAGE_BASE"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api  = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(
    bearer_token, consumer_key, consumer_secret,
    access_token, access_token_secret,
    wait_on_rate_limit=True,
)

def build_image_url(token_id: str) -> str:
    token_padded = "{:05d}".format(int(token_id))
    return f"{CF_IMAGE_BASE}/{token_padded}.png"

def tweet_image(image_url: str, message: str):
    filename = "/tmp/temp.png"
    try:
        r = requests.get(image_url, stream=True, timeout=30)
        if r.status_code != 200:
            print(f"Could not download image (HTTP {r.status_code})")
            client.create_tweet(text=message)
            return
        with open(filename, "wb") as f:
            for chunk in r:
                f.write(chunk)
        media_id = api.media_upload(filename=filename).media_id_string
        client.create_tweet(text=message, media_ids=[media_id])
        os.remove(filename)
        print("Tweeted!")
    except Exception as e:
        print(f"Tweet failed: {e}")

def send_discord(message: str, image_url: str):
    data = {
        "content": message,
        "embeds": [{"image": {"url": image_url}}],
    }
    try:
        result = requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
        result.raise_for_status()
    except Exception as e:
        print(f"Discord post failed: {e}")

def send_tweet(sale: dict, collection: str, contract: str, chain: str, eth_spot: float):
    token_id  = sale["token_id"]
    eth       = sale["eth"]
    usd       = eth * eth_spot
    if usd == 0:
        return
    opensea_url = f"https://opensea.io/item/{chain}/{contract}/{token_id}"
    image_url   = build_image_url(token_id)
    message = (
        f"{collection} #{token_id} just sold!\n\n"
        f"Price: {eth:.4f} $ETH (${usd:.2f} $USD)\n\n"
        f"{opensea_url}\n\n"
        f"Marketplace: OpenSea\n\n"
        f"#Shibui #PiratesOfFukushu #NFT❗️"
    )
    tweet_image(image_url, message)
    try:
        send_discord(message, image_url)
    except Exception as e:
        print(f"Could not send to Discord: {e}")

print("Tweet module loaded.")
