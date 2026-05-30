from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskLabel = Literal["SAFE", "SPAM", "PII_LEAK", "HARASSMENT", "NSFW", "OTHER"]


@dataclass
class RedditPost:
    id: str
    author: str
    title: str
    selftext: str
    ups: int
    permalink: str

    @classmethod
    def from_raw(cls, raw: dict) -> "RedditPost":
        return cls(
            id=str(raw.get("id", "")),
            author=str(raw.get("author", "")),
            title=str(raw.get("title", "")),
            selftext=str(raw.get("selftext", "")),
            ups=int(raw.get("ups", 0) or 0),
            permalink=str(raw.get("permalink", "")),
        )

    def to_row(self) -> tuple:
        return (self.id, self.author, self.title, self.selftext, self.ups, self.permalink)
