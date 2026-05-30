from __future__ import annotations

import sqlite3
from typing import Iterable

from .models import RedditPost

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS reddit_posts (
    id TEXT PRIMARY KEY,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    selftext TEXT NOT NULL,
    ups INTEGER NOT NULL,
    permalink TEXT NOT NULL
);
"""


def build_connection(posts: Iterable[RedditPost]) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(CREATE_SQL)
    conn.executemany(
        "INSERT OR REPLACE INTO reddit_posts (id, author, title, selftext, ups, permalink) VALUES (?, ?, ?, ?, ?, ?);",
        [p.to_row() for p in posts],
    )
    conn.commit()
    return conn


def query_low_upvote_posts(conn: sqlite3.Connection, max_ups: int = 10) -> list[tuple]:
    sql = "SELECT id, author, title, selftext, ups FROM reddit_posts WHERE ups < ? ORDER BY ups ASC, id ASC;"
    cursor = conn.execute(sql, (max_ups,))
    return cursor.fetchall()


def query_all_posts(conn: sqlite3.Connection) -> list[tuple]:
    cursor = conn.execute(
        "SELECT id, author, title, selftext, ups, permalink FROM reddit_posts ORDER BY ups ASC, id ASC;"
    )
    return cursor.fetchall()
