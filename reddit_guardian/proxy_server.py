from pathlib import Path
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from fastapi import FastAPI, Query

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_JSON = BASE_DIR / "sample_reddit_response.json"


@app.get("/healthz")
def healthz():
    return {"ok": True}


def fetch_reddit_json(subreddit: str):
    url = f"https://www.reddit.com/r/{subreddit}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Reddit Guardian Agent; hackathon demo)"
    }

    req = Request(url, headers=headers)

    try:
        with urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        with SAMPLE_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        with SAMPLE_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)


@app.get("/reddit.json")
def reddit_json(subreddit: str = Query(default="TikTokCringe")):
    return fetch_reddit_json(subreddit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("reddit_guardian.proxy_server:app", host="127.0.0.1", port=8787, reload=False)