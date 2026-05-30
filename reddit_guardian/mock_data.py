from __future__ import annotations

import json
from pathlib import Path

from .coral_connector import load_reddit_posts_from_json


def load_sample_posts() -> list:
    sample_path = Path(__file__).with_name("sample_reddit_response.json")
    return load_reddit_posts_from_json(json.loads(sample_path.read_text(encoding="utf-8")))
