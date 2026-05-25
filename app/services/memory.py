from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from app.services.storage_paths import MEMORY_DIR, ensure_data_dirs

DB_PATH = MEMORY_DIR / "memory.db"


def _connect() -> sqlite3.Connection:
    ensure_data_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            source_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS approved_hooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hook TEXT NOT NULL,
            mode TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS rejected_theses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thesis TEXT NOT NULL,
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )
    conn.commit()
    return conn


def add_favorite(*, url: str, title: str = "", source_type: str = "") -> dict[str, Any]:
    conn = _connect()
    conn.execute(
        "INSERT INTO favorites (url, title, source_type) VALUES (?, ?, ?)",
        (url, title, source_type),
    )
    conn.commit()
    conn.close()
    return {"url": url, "title": title, "source_type": source_type}


def list_favorites(*, limit: int = 50) -> list[dict[str, Any]]:
    conn = _connect()
    rows = conn.execute(
        "SELECT url, title, source_type, created_at FROM favorites ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_approved_hook(hook: str, *, mode: str = "") -> None:
    conn = _connect()
    conn.execute("INSERT INTO approved_hooks (hook, mode) VALUES (?, ?)", (hook, mode))
    conn.commit()
    conn.close()


def get_recent_hooks(*, limit: int = 10) -> list[str]:
    conn = _connect()
    rows = conn.execute(
        "SELECT hook FROM approved_hooks ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [row["hook"] for row in rows]


def set_preference(key: str, value: Any) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO preferences (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(value)),
    )
    conn.commit()
    conn.close()


def get_preference(key: str, default: Any = None) -> Any:
    conn = _connect()
    row = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
    conn.close()
    if not row:
        return default
    try:
        return json.loads(row["value"])
    except json.JSONDecodeError:
        return row["value"]
