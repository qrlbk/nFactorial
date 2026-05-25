from __future__ import annotations

from typing import Any

from app.i18n import output_language_name
from app.schemas.rewrite import RewriteOutput
from app.services.llm import invoke_structured
from app.utils.tweet_sanitize import sanitize_tweets


async def qrt_writer_node(state: dict[str, Any]) -> dict[str, Any]:
    result = await invoke_structured(
        node_name="qrt_writer",
        prompt_name="qrt_writer",
        input_vars={
            "mode": state.get("selected_mode", "Contrarian VC"),
            "output_language": state.get("output_language", "en"),
            "output_language_name": output_language_name(state.get("output_language", "en")),
            "quoted_tweet": state.get("quoted_tweet", ""),
            "thesis_position": state.get("thesis_position", {}),
            "distilled_context": state.get("distilled_context", {}),
            "critic_feedback": (state.get("last_critic_report") or {}).get("verdict", "None"),
        },
        output_schema=RewriteOutput,
    )
    tweets = sanitize_tweets(result.tweets[:1])
    log = list(state.get("pipeline_log", []))
    log.append("[QRTWriter] DONE")
    return {
        "current_tweets": tweets,
        "current_draft": tweets[0] if tweets else "",
        "pipeline_log": log,
    }
