from __future__ import annotations

import hashlib
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from app.services.storage_paths import CHUNKS_DIR, ensure_data_dirs

DB_PATH = CHUNKS_DIR / "chunks.db"


def _connect() -> sqlite3.Connection:
    ensure_data_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            chunk_id UNINDEXED,
            source_url UNINDEXED,
            source_title,
            content,
            tokenize='porter'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunk_meta (
            chunk_id TEXT PRIMARY KEY,
            source_url TEXT,
            source_title TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def _chunk_text(text: str, *, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    words = re.split(r"\s+", text.strip())
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size)
        piece = " ".join(words[start:end]).strip()
        if piece:
            chunks.append(piece)
        if end >= len(words):
            break
        start = max(0, end - overlap)
    return chunks


def store_document(
    *,
    text: str,
    source_url: str = "",
    source_title: str = "",
) -> list[dict[str, Any]]:
    conn = _connect()
    stored: list[dict[str, Any]] = []
    for idx, content in enumerate(_chunk_text(text)):
        chunk_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO chunk_meta (chunk_id, source_url, source_title) VALUES (?, ?, ?)",
            (chunk_id, source_url, source_title),
        )
        conn.execute(
            "INSERT INTO chunks_fts (chunk_id, source_url, source_title, content) VALUES (?, ?, ?, ?)",
            (chunk_id, source_url, source_title, content),
        )
        stored.append(
            {
                "chunk_id": chunk_id,
                "source_url": source_url,
                "source_title": source_title,
                "content": content,
                "index": idx,
            }
        )
    conn.commit()
    conn.close()
    return stored


def retrieve_chunks(query: str, *, limit: int = 8) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    conn = _connect()
    safe_query = " OR ".join(f'"{tok}"' for tok in query.split() if len(tok) > 2) or f'"{query[:80]}"'
    rows = conn.execute(
        """
        SELECT chunk_id, source_url, source_title, content,
               bm25(chunks_fts) AS rank
        FROM chunks_fts
        WHERE chunks_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (safe_query, limit),
    ).fetchall()
    conn.close()
    return [
        {
            "chunk_id": row["chunk_id"],
            "source_url": row["source_url"],
            "source_title": row["source_title"],
            "content": row["content"],
            "rank": row["rank"],
        }
        for row in rows
    ]


def cache_key(source: str, query: str) -> str:
    raw = f"{source}:{query}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]
