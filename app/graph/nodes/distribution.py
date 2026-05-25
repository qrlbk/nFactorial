from __future__ import annotations

from typing import Any

from app.services.distribution.publisher import create_launch_draft


async def distribution_node(state: dict[str, Any]) -> dict[str, Any]:
    output_type = state.get("output_type", "thread")
    tweets = state.get("final_elite_thread") or state.get("current_tweets") or []
    essay = state.get("current_draft", "")
    content: list[str] | str
    if output_type in ("essay", "article"):
        content = essay
    else:
        content = tweets

    draft = create_launch_draft(
        output_type=output_type,
        content=content,
        mode=state.get("selected_mode", "Contrarian VC"),
        trace_id=state.get("trace_id"),
    )
    log = list(state.get("pipeline_log", []))
    log.append(f"[Distribution] QUEUED {draft['id']}")
    final_output = dict(state.get("final_output") or {})
    final_output["launch_draft_id"] = draft["id"]
    return {"final_output": final_output, "pipeline_log": log}
