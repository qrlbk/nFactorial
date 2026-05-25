from typing import Literal

from app.config import get_settings


def route_after_context_gate(state: dict) -> Literal["retrieval", "research", "refuse"]:
    if state.get("context_qualified") is False or state.get("refusal_reason"):
        return "refuse"
    if state.get("source_urls") or state.get("autonomous_research"):
        return "retrieval"
    return "research"


def route_after_thesis_angles(state: dict) -> Literal["thesis", "narrative", "writer", "end", "refuse"]:
    if state.get("refusal_reason"):
        return "refuse"
    if state.get("thesis_only"):
        return "end"
    if state.get("thesis_candidates") and not state.get("selected_thesis_id"):
        return "end"
    if state.get("thesis_position"):
        if state.get("output_type") == "quote_retweet":
            return "writer"
        return "narrative"
    return "thesis"


def route_after_thesis(state: dict) -> Literal["narrative", "writer", "refuse"]:
    if state.get("refusal_reason"):
        return "refuse"
    if state.get("output_type") == "quote_retweet":
        return "writer"
    return "narrative"


def route_after_narrative(state: dict) -> Literal["writer"]:
    return "writer"


def route_after_writer(state: dict) -> Literal["evaluators"]:
    return "evaluators"


def route_after_context_gate_legacy(state: dict) -> Literal["research", "refuse"]:
    if state.get("context_qualified") is False or state.get("refusal_reason"):
        return "refuse"
    return "research"


def route_after_thesis_legacy(state: dict) -> Literal["narrative", "refuse"]:
    if state.get("refusal_reason"):
        return "refuse"
    return "narrative"


def route_after_evaluators(state: dict) -> Literal["critic", "writer", "refuse"]:
    settings = get_settings()
    if state.get("total_retry_count", 0) >= settings.max_critic_retries:
        return "refuse"
    if state.get("eval_passed"):
        return "critic"
    return "writer"


def route_after_critic(state: dict) -> Literal["end", "writer", "refuse", "post"]:
    settings = get_settings()
    if state.get("total_retry_count", 0) >= settings.max_critic_retries:
        return "refuse"

    report = state.get("last_critic_report", {})
    if report.get("decision") == "APPROVED":
        if state.get("skip_post_pipeline"):
            return "end"
        return "post"
    return "writer"


def route_after_fact_check(state: dict) -> Literal["hooks", "writer", "refuse"]:
    settings = get_settings()
    report = state.get("fact_check_report") or {}
    if report.get("passed") is False:
        if state.get("total_retry_count", 0) >= settings.max_critic_retries:
            return "refuse"
        total_retry = state.get("total_retry_count", 0) + 1
        state["total_retry_count"] = total_retry
        return "writer"
    return "hooks"


def route_after_rewrite(state: dict) -> Literal["evaluators"]:
    return "evaluators"
