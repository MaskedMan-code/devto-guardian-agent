from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import RedditPost


def load_reddit_posts_from_json(payload: dict[str, Any]) -> list[RedditPost]:
    """Parse the Reddit listing shape: data.children[index].data."""
    children = (((payload or {}).get("data") or {}).get("children")) or []
    posts: list[RedditPost] = []

    for child in children:
        data = child.get("data", {}) if isinstance(child, dict) else {}
        if not isinstance(data, dict):
            continue
        if "id" not in data:
            continue
        posts.append(RedditPost.from_raw(data))

    return posts


def load_reddit_posts_from_path(path: str | Path) -> list[RedditPost]:
    path = Path(path)
    return load_reddit_posts_from_json(json.loads(path.read_text(encoding="utf-8")))


def coral_connector_yaml() -> str:
    return """name: reddit_guardian
version: 1.0.1
dsl_version: 3
backend: http

inputs:
  TARGET_SUBREDDIT:
    kind: variable
    default: TikTokCringe
    hint: "Subreddit name without /r/ (for example: TikTokCringe)"

base_url: "http://127.0.0.1:8787"

test_queries:
  - SELECT id, author, title, selftext, ups, permalink FROM reddit_guardian.posts LIMIT 5

tables:
  - name: posts
    description: Raw Reddit posts fetched through the local proxy endpoint
    request:
      method: GET
      path: /reddit.json?subreddit={{input.TARGET_SUBREDDIT}}
    response:
      rows_path:
        - data
        - children
    columns:
      - name: id
        type: Utf8
        expr:
          kind: path
          path:
            - data
            - id
      - name: author
        type: Utf8
        expr:
          kind: path
          path:
            - data
            - author
      - name: title
        type: Utf8
        expr:
          kind: path
          path:
            - data
            - title
      - name: selftext
        type: Utf8
        expr:
          kind: path
          path:
            - data
            - selftext
      - name: ups
        type: Int64
        expr:
          kind: path
          path:
            - data
            - ups
      - name: permalink
        type: Utf8
        expr:
          kind: path
          path:
            - data
            - permalink
"""
