from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.schemas.platform import DiscoveryItem, SourceType
from app.services.chunk_store import cache_key
from app.services.storage_paths import DISCOVERY_DIR, ensure_data_dirs

DISCOVERY_TTL_SECONDS = 6 * 3600


def _cache_path(source: str, query: str) -> Path:
    ensure_data_dirs()
    return DISCOVERY_DIR / f"{cache_key(source, query)}.json"


def read_cache(source: str, query: str) -> list[DiscoveryItem] | None:
    path = _cache_path(source, query)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    cached_at = datetime.fromisoformat(data["cached_at"])
    if (datetime.now(timezone.utc) - cached_at).total_seconds() > DISCOVERY_TTL_SECONDS:
        return None
    return [DiscoveryItem(**item) for item in data.get("items", [])]


def write_cache(source: str, query: str, items: list[DiscoveryItem]) -> None:
    path = _cache_path(source, query)
    payload = {
        "source": source,
        "query": query,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "items": [item.model_dump() for item in items],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


async def discover(source: SourceType | str, query: str, *, max_results: int = 10) -> tuple[list[DiscoveryItem], bool]:
    cached = read_cache(source, query)
    if cached is not None:
        return cached[:max_results], True

    if source == "arxiv":
        from app.services.discovery.arxiv_fetcher import search_arxiv

        items = await search_arxiv(query, max_results=max_results)
    elif source == "hackernews":
        from app.services.discovery.hn_fetcher import search_hn

        items = await search_hn(query, max_results=max_results)
    elif source == "substack":
        from app.services.discovery.substack_fetcher import search_substack

        items = await search_substack(query, max_results=max_results)
    elif source == "tweets":
        from app.services.discovery.tweet_curator import trending_tweets

        items = trending_tweets(query, max_results=max_results)
    else:
        items = []

    write_cache(source, query, items)
    return items[:max_results], False
