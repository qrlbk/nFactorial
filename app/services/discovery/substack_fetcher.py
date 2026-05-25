from __future__ import annotations

import feedparser
import httpx

from app.schemas.platform import DiscoveryItem

# Curated tech/research Substack RSS feeds for discovery
DEFAULT_FEEDS = [
    "https://www.oneusefulthing.org/feed",
    "https://stratechery.com/feed/",
    "https://www.interconnects.ai/feed",
]


async def search_substack(query: str, *, max_results: int = 10) -> list[DiscoveryItem]:
    q = query.lower()
    items: list[DiscoveryItem] = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for feed_url in DEFAULT_FEEDS:
            try:
                resp = await client.get(feed_url, follow_redirects=True)
                resp.raise_for_status()
                parsed = feedparser.parse(resp.text)
            except httpx.HTTPError:
                continue
            for entry in parsed.entries:
                title = getattr(entry, "title", "") or ""
                summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
                link = getattr(entry, "link", "") or ""
                blob = f"{title} {summary}".lower()
                if q not in blob and not any(tok in blob for tok in q.split() if len(tok) > 3):
                    continue
                items.append(
                    DiscoveryItem(
                        title=title[:200],
                        url=link,
                        excerpt=summary[:400],
                        source_type="substack",
                        published_at=getattr(entry, "published", None),
                        relevance_score=0.75,
                        author=getattr(entry, "author", None),
                    )
                )
    items.sort(key=lambda x: x.relevance_score, reverse=True)
    return items[:max_results]
