from __future__ import annotations

from app.graph.builder import run_pipeline
from app.services.discovery import discover


async def run_autonomous_research(
    *,
    topic: str,
    mode: str = "Contrarian VC",
    output_type: str = "thread",
    output_language: str = "en",
    response_locale: str = "en",
    auto_pick_thesis: bool = True,
    source_urls: list[str] | None = None,
) -> dict:
    items, _ = await discover("arxiv", topic, max_results=3)
    items_hn, _ = await discover("hackernews", topic, max_results=3)
    all_items = items + items_hn
    urls = list(source_urls or [])
    urls.extend(item.url for item in all_items if item.url and item.url not in urls)

    briefing = f"Research topic: {topic}\n\n"
    for item in all_items[:6]:
        briefing += f"## {item.title}\n{item.excerpt}\nSource: {item.url}\n\n"

    selected_thesis_id = None

    if auto_pick_thesis:
        angles_result = await run_pipeline(
            raw_context=briefing,
            mode=mode,
            output_language=output_language,
            response_locale=response_locale,
            output_type=output_type,  # type: ignore[arg-type]
            source_urls=urls,
            autonomous_research=True,
            research_topic=topic,
            thesis_only=True,
            generate_thesis_angles=True,
            skip_post_pipeline=True,
        )
        candidates = angles_result.get("thesis_candidates") or []
        if candidates:
            best = max(candidates, key=lambda c: c.get("thesis_confidence", 0))
            selected_thesis_id = best.get("id")
        briefing = angles_result.get("raw_context", briefing)

    return await run_pipeline(
        raw_context=briefing,
        mode=mode,
        output_language=output_language,
        response_locale=response_locale,
        output_type=output_type,  # type: ignore[arg-type]
        source_urls=urls,
        autonomous_research=True,
        research_topic=topic,
        selected_thesis_id=selected_thesis_id,
        generate_thesis_angles=bool(selected_thesis_id),
    )
