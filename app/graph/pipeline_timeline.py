from __future__ import annotations

from typing import Any

from app.i18n import t


def infer_status(node: str, result: dict[str, Any], prior_log: list[str]) -> str:
    log = result.get("pipeline_log", prior_log)
    if node == "context_qualification_gate":
        if result.get("context_qualified") is False:
            return "refused"
        if result.get("borderline_input"):
            return "borderline"
        return "qualified"
    if node == "thesis_commitment":
        if result.get("refusal_reason") and not result.get("narrative_completed"):
            for line in reversed(log):
                if line.startswith("[Thesis]") and "REFUSED" in line:
                    return "refused"
        return "done"
    if node == "deterministic_evaluators":
        return "passed" if result.get("eval_passed") else "rejected"
    if node == "anti_slop_critic":
        report = result.get("last_critic_report") or {}
        decision = str(report.get("decision", "")).upper()
        if decision == "APPROVED":
            return "approved"
        return "rejected"
    if node == "high_pressure_rewriter":
        for line in reversed(log):
            if "[Rewrite] RETRY" in line:
                return "retry"
        return "done"
    if node == "refuse":
        return "fail_closed"
    return "done"


def infer_detail(node: str, result: dict[str, Any], prior_state: dict[str, Any]) -> str:
    locale = prior_state.get("response_locale", "en")

    if node == "context_qualification_gate":
        score = result.get("input_worthiness_score", prior_state.get("input_worthiness_score", 0))
        if result.get("context_qualified") is False:
            reasons = result.get("rejection_history", [])
            if reasons:
                return reasons[-1].get("reason", t(locale, "pipeline.detail.gate_refused"))[:120]
            return t(locale, "pipeline.detail.gate_refused")
        return t(locale, "pipeline.detail.gate_worthiness", score=f"{score:.2f}")

    if node == "research_distiller":
        distilled = result.get("distilled_context") or prior_state.get("distilled_context") or {}
        anchors = len(distilled.get("causal_anchors") or [])
        questions = len(distilled.get("open_questions") or [])
        return t(locale, "pipeline.detail.research", anchors=anchors, questions=questions)

    if node == "thesis_commitment":
        thesis = result.get("thesis_position") or prior_state.get("thesis_position") or {}
        conf = thesis.get("thesis_confidence")
        if conf is not None:
            return t(locale, "pipeline.detail.thesis_confidence", confidence=f"{conf:.2f}")
        return t(locale, "pipeline.detail.thesis_committed")

    if node == "narrative_architect":
        frame = result.get("narrative_frame") or prior_state.get("narrative_frame") or {}
        points = len(frame.get("escalation_points") or [])
        return t(locale, "pipeline.detail.narrative", points=points)

    if node == "high_pressure_rewriter":
        tweets = result.get("current_tweets") or prior_state.get("current_tweets") or []
        attempt = result.get("rewrite_attempts", prior_state.get("rewrite_attempts", 0))
        label = (
            t(locale, "pipeline.detail.rewrite_retry", attempt=attempt - 1)
            if attempt > 1
            else t(locale, "pipeline.detail.rewrite_draft")
        )
        return t(locale, "pipeline.detail.rewrite", count=len(tweets), label=label)

    if node == "deterministic_evaluators":
        if result.get("eval_passed"):
            return t(locale, "pipeline.detail.eval_passed")
        history = result.get("rejection_history") or prior_state.get("rejection_history") or []
        for event in reversed(history):
            if event.get("node") == "deterministic_evaluators":
                return event.get("reason", t(locale, "pipeline.detail.eval_rejected"))[:120]
        return t(locale, "pipeline.detail.eval_rejected")

    if node == "anti_slop_critic":
        report = result.get("last_critic_report") or prior_state.get("last_critic_report") or {}
        if str(report.get("decision", "")).upper() == "APPROVED":
            return report.get("verdict", t(locale, "pipeline.detail.critic_approved"))[:120]
        phrases = report.get("slop_phrases_found") or []
        if phrases:
            return t(locale, "pipeline.detail.critic_slop", phrases=", ".join(phrases[:3]))
        return report.get("reasoning_flaw", t(locale, "pipeline.detail.eval_rejected"))[:120]

    if node == "refuse":
        return t(locale, "pipeline.detail.quality_failed")

    return ""


def append_timeline_entry(
    *,
    timeline: list[dict[str, Any]],
    node: str,
    status: str,
    duration_ms: int,
    detail: str,
) -> list[dict[str, Any]]:
    return [
        *timeline,
        {"node": node, "status": status, "duration_ms": duration_ms, "detail": detail},
    ]


def append_thread_assembler(
    timeline: list[dict[str, Any]], tweet_count: int, *, locale: str = "en"
) -> list[dict[str, Any]]:
    if tweet_count <= 0:
        return timeline
    return [
        *timeline,
        {
            "node": "thread_assembler",
            "status": "done",
            "duration_ms": 0,
            "detail": t(locale, "pipeline.detail.assembled", count=tweet_count),
        },
    ]
