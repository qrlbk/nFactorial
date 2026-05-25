from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from app.schemas.platform import DiscoveryItem

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


async def search_arxiv(query: str, *, max_results: int = 10) -> list[DiscoveryItem]:
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)

    items: list[DiscoveryItem] = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        title = (entry.findtext("atom:title", default="", namespaces=ARXIV_NS) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ARXIV_NS) or "").strip()
        link_el = entry.find("atom:id", ARXIV_NS)
        paper_url = link_el.text.strip() if link_el is not None and link_el.text else ""
        published = entry.findtext("atom:published", default=None, namespaces=ARXIV_NS)
        authors = [
            a.findtext("atom:name", default="", namespaces=ARXIV_NS)
            for a in entry.findall("atom:author", ARXIV_NS)
        ]
        items.append(
            DiscoveryItem(
                title=title.replace("\n", " "),
                url=paper_url,
                excerpt=summary[:400],
                source_type="arxiv",
                published_at=published,
                relevance_score=0.85,
                author=", ".join(a for a in authors if a)[:120] or None,
            )
        )
    return items
