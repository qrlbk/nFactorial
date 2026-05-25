from __future__ import annotations

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.services.chunk_store import retrieve_chunks, store_document


async def fetch_url_text(url: str) -> tuple[str, str]:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "EditorialOS/1.0"})
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "html" in content_type:
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            title = (soup.title.string if soup.title else url) or url
            text = soup.get_text(separator="\n")
            text = re.sub(r"\n{3,}", "\n\n", text)
            return str(title).strip(), text.strip()
        return url, resp.text.strip()


async def ingest_url(url: str, *, title: str = "") -> dict[str, Any]:
    fetched_title, text = await fetch_url_text(url)
    doc_title = title or fetched_title
    chunks = store_document(text=text, source_url=url, source_title=doc_title)
    preview = text[:500]
    return {
        "url": url,
        "title": doc_title,
        "chunk_count": len(chunks),
        "preview": preview,
        "chunks": chunks[:5],
    }


async def retrieval_node(state: dict[str, Any]) -> dict[str, Any]:
    log = list(state.get("pipeline_log", []))
    source_urls = list(state.get("source_urls") or [])
    retrieved: list[dict[str, Any]] = []
    source_documents: list[dict[str, Any]] = []

    for url in source_urls:
        try:
            doc = await ingest_url(url)
            source_documents.append(doc)
            retrieved.extend(doc.get("chunks") or [])
        except httpx.HTTPError as exc:
            log.append(f"[Retrieval] WARN failed {url}: {exc}")

    query = state.get("research_topic") or state.get("raw_context", "")[:300]
    if query.strip():
        retrieved.extend(retrieve_chunks(query, limit=8))

    context_addition = ""
    if retrieved:
        context_addition = "\n\n--- RETRIEVED SOURCES ---\n" + "\n\n".join(
            f"[{c.get('chunk_id', 'chunk')}] {c.get('content', '')[:800]}"
            for c in retrieved[:8]
        )

    raw_context = state.get("raw_context", "")
    if context_addition and context_addition not in raw_context:
        raw_context = raw_context + context_addition

    log.append(f"[Retrieval] DONE ({len(retrieved)} chunks)")
    return {
        "raw_context": raw_context,
        "retrieved_chunks": retrieved,
        "source_documents": source_documents,
        "pipeline_log": log,
    }
