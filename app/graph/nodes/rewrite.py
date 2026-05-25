from typing import Any

import re

from app.i18n import output_language_name
from app.schemas.rewrite import RewriteOutput
from app.services.llm import invoke_structured
from app.utils.tweet_sanitize import sanitize_tweets


_EVALUATOR_HINTS: dict[str, str] = {
    "Mechanism layers": (
        "REQUIRED: ≥2 tweets (one per line) with (causal: because/bc/forces/drives/—) "
        "AND (mechanism: cost/inference/GPU/CUDA/pricing/margin) in the SAME tweet, "
        "OR number + mechanism (e.g. 10x + parameter count)."
    ),
    "Specificity score": (
        "REQUIRED: include ≥2 distinct numbers and ≥1 named system (RAG, GPU, CUDA, embedding, "
        "500 docs, 200k, 10x, etc.) from causal_anchors in the thread — one concrete stat per tweet."
    ),
    "Defended claim overlap": (
        "REQUIRED: reuse defended_claim keywords in the first 2 tweets."
    ),
}


def _evaluator_feedback(state: dict[str, Any]) -> str:
    history = state.get("rejection_history") or []
    for event in reversed(history):
        if event.get("node") == "deterministic_evaluators" and event.get("reason"):
            reason = str(event["reason"])
            hints = [hint for key, hint in _EVALUATOR_HINTS.items() if key in reason]
            if "Specificity score" in reason:
                anchors = state.get("distilled_context", {}).get("causal_anchors") or []
                nums = []
                for a in anchors:
                    for key in ("value", "metric", "subject"):
                        v = a.get(key)
                        if v and re.search(r"\d", str(v)):
                            nums.append(str(v))
                if nums:
                    hints.append(f"USE THESE NUMBERS FROM ANCHORS: {', '.join(nums[:6])}")
            if "Mechanism layers" in reason:
                anchors = state.get("distilled_context", {}).get("causal_anchors") or []
                examples = []
                for a in anchors[:2]:
                    subj = a.get("subject", "")
                    metric = a.get("metric", "")
                    val = a.get("value", "")
                    if subj and metric:
                        examples.append(
                            f'Example tweet: "{subj} {metric} {val} because [mechanism from anchors]."'
                        )
                if examples:
                    hints.append("ANCHOR EXAMPLES:\n" + "\n".join(examples))
            if hints:
                return reason + "\n\nFIX:\n" + "\n".join(f"- {h}" for h in hints)
            return reason
    return "None — pass evaluators on next attempt."


def _critic_feedback(state: dict[str, Any]) -> str:
    report = state.get("last_critic_report") or {}
    if report.get("decision") != "REJECTED":
        return "None — first rewrite pass."
    parts = [report.get("verdict", ""), report.get("reasoning_flaw", "")]
    slop = report.get("slop_phrases_found") or []
    if slop:
        parts.append("Slop phrases to remove: " + ", ".join(slop))
    return "\n".join(p for p in parts if p.strip())


async def high_pressure_rewriter_node(state: dict[str, Any]) -> dict[str, Any]:
    narrative = state.get("narrative_frame", {})
    rewrite_attempts = state.get("rewrite_attempts", 0) + 1

    result = await invoke_structured(
        node_name="high_pressure_rewriter",
        prompt_name="rewrite",
        input_vars={
            "mode": state.get("selected_mode", "Contrarian VC"),
            "output_language": state.get("output_language", "en"),
            "output_language_name": output_language_name(state.get("output_language", "en")),
            "thesis_position": state["thesis_position"],
            "narrative_frame": narrative if narrative else {},
            "insight_anchors": state.get("distilled_context", {}).get("insight_anchors", []),
            "causal_anchors": state.get("distilled_context", {}).get("causal_anchors", []),
            "open_questions": state.get("distilled_context", {}).get("open_questions", []),
            "voice_guidelines": state.get("voice_guidelines", {}),
            "current_draft": state.get("current_draft", ""),
            "critic_feedback": _critic_feedback(state),
            "evaluator_feedback": _evaluator_feedback(state),
        },
        output_schema=RewriteOutput,
    )

    tweets = sanitize_tweets(result.tweets)
    draft_text = "\n\n".join(f"{i + 1}/ {tweet}" for i, tweet in enumerate(tweets))
    log = list(state.get("pipeline_log", []))
    if rewrite_attempts > 1:
        log.append(f"[Rewrite] RETRY #{rewrite_attempts - 1}")
    else:
        log.append("[Rewrite] DONE")

    return {
        "current_tweets": tweets,
        "current_draft": draft_text,
        "rewrite_attempts": rewrite_attempts,
        "pipeline_log": log,
    }
