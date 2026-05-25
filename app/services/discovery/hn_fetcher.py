from __future__ import annotations

import httpx

from app.schemas.platform import DiscoveryItem


async def search_hn(query: str, *, max_results: int = 10) -> list[DiscoveryItem]:
    url = "https://hn.algolia.com/api/v1/search"
    params = {"query": query, "tags": "story", "hitsPerPage": max_results}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    items: list[DiscoveryItem] = []
    for hit in data.get("hits", []):
        object_id = hit.get("objectID", "")
        story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
        items.append(
            DiscoveryItem(
                title=hit.get("title") or "HN story",
                url=story_url,
                excerpt=(hit.get("story_text") or hit.get("comment_text") or hit.get("title") or "")[:400],
                source_type="hackernews",
                published_at=hit.get("created_at"),
                relevance_score=min(1.0, (hit.get("points") or 0) / 500 + 0.3),
                author=hit.get("author"),
            )
        )
    return items
