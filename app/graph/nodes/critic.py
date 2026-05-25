from datetime import datetime, timezone
from typing import Any

from app.schemas.criticism import CriticismReport
from app.schemas.trace import RejectionEvent
from app.services.llm import invoke_structured
from app.services.tracing import log_rejection
from app.utils.relational_consistency import evaluate_relational_consistency
from app.utils.semantic_density import evaluate_semantic_density


def _deterministic_critic_veto(state: dict[str, Any]) -> str | None:
    """Skepticism-first: reject obvious relation drift before LLM critic."""
    tweets = state.get("current_tweets", [])
    causal = state.get("distilled_context", {}).get("causal_anchors", [])
    if tweets and causal:
        rel = evaluate_relational_consistency(tweets, causal)
        if not rel.passed:
            return rel.reasons[0]
    return None


def _evaluator_certified_approve(state: dict[str, Any]) -> bool:
    """When deterministic evaluators passed, skip subjective LLM reject on later attempts."""
    if not state.get("eval_passed"):
        return False
    draft_attempt = state.get("rewrite_attempts", 1)
    if draft_attempt < 2:
        return False
    tweets = state.get("current_tweets", [])
    if not tweets:
        return False
    rel = evaluate_relational_consistency(
        tweets,
        state.get("distilled_context", {}).get("causal_anchors", []),
    )
    if not rel.passed:
        return False
    return evaluate_semantic_density("\n".join(tweets)).passed


async def anti_slop_critic_node(
    state: dict[str, Any],
    *,
    trace: Any = None,
) -> dict[str, Any]:
    log = list(state.get("pipeline_log", []))
    rejection_history = list(state.get("rejection_history", []))
    critic_attempts = state.get("critic_attempts", 0)
    total_retry = state.get("total_retry_count", 0)

    # Deterministic veto — no LLM laundering
    veto = _deterministic_critic_veto(state)
    if veto:
        critic_attempts += 1
        total_retry += 1
        event = RejectionEvent(
            node="anti_slop_critic",
            timestamp=datetime.now(timezone.utc),
            reason=veto,
            failed_metrics={"deterministic_veto": True, "type": "relational_drift"},
            rejected_excerpt=state.get("current_draft", "")[:300],
        )
        rejection_history.append(event.model_dump(mode="json"))
        log.append("[Critic] REJECTED (deterministic)")
        log.append(f"Reason: - {veto}")
        log_rejection(
            trace,
            node="anti_slop_critic",
            reason=veto,
            failed_metrics=event.failed_metrics,
            rejected_excerpt=event.rejected_excerpt,
            retry_count=total_retry,
        )
        return {
            "last_critic_report": {
                "decision": "REJECTED",
                "cliche_detected": False,
                "reasoning_flaw": veto,
                "slop_phrases_found": [],
                "verdict": f"REJECTED: {veto}",
            },
            "critic_attempts": critic_attempts,
            "total_retry_count": total_retry,
            "rejection_history": rejection_history,
            "pipeline_log": log,
        }

    borderline = state.get("borderline_input", False)
    strictness = state.get("critic_strictness_boost", 0.0)
    draft_attempt = state.get("rewrite_attempts", 1)

    if _evaluator_certified_approve(state):
        log.append("[Critic] APPROVED (evaluator-certified draft)")
        report = CriticismReport(
            decision="APPROVED",
            cliche_detected=False,
            reasoning_flaw="",
            slop_phrases_found=[],
            verdict="APPROVED: passed deterministic evaluators + semantic density on retry",
        )
        return {
            "last_critic_report": report.model_dump(),
            "critic_attempts": critic_attempts,
            "total_retry_count": total_retry,
            "rejection_history": rejection_history,
            "pipeline_log": log,
            "final_elite_thread": state.get("current_tweets", []),
        }

    result = await invoke_structured(
        node_name="anti_slop_critic",
        prompt_name="critic",
        input_vars={
            "thesis_position": state["thesis_position"],
            "current_draft": state.get("current_draft", ""),
            "borderline_mode": (
                f"BORDERLINE INPUT — apply +{strictness:.0%} skepticism. "
                "Assume first draft guilty. Reject unless domain expert would repost."
                if borderline
                else "Standard skepticism — assume first draft guilty until proven insightful."
            ),
            "draft_attempt": draft_attempt,
        },
        output_schema=CriticismReport,
    )

    # Skepticism prior: on first critic pass, require stronger verdict for APPROVE
    if result.decision == "APPROVED" and draft_attempt <= 1 and borderline:
        result = CriticismReport(
            decision="REJECTED",
            cliche_detected=result.cliche_detected,
            reasoning_flaw=(
                "Borderline input with first draft — insufficient epistemic value "
                "for automatic approval under elevated strictness"
            ),
            slop_phrases_found=result.slop_phrases_found,
            verdict="REJECTED: borderline input requires sharper non-obvious insight",
        )

    if result.decision == "REJECTED":
        critic_attempts += 1
        total_retry += 1
        event = RejectionEvent(
            node="anti_slop_critic",
            timestamp=datetime.now(timezone.utc),
            reason=result.verdict,
            failed_metrics={
                "cliche_detected": result.cliche_detected,
                "reasoning_flaw": result.reasoning_flaw,
                "slop_phrases": result.slop_phrases_found,
                "borderline": borderline,
            },
            rejected_excerpt=state.get("current_draft", "")[:300],
        )
        rejection_history.append(event.model_dump(mode="json"))
        log.append("[Critic] REJECTED")
        log.append("Reason:")
        for phrase in result.slop_phrases_found[:5]:
            log.append(f"- {phrase}")
        if result.reasoning_flaw:
            log.append(f"- {result.reasoning_flaw}")

        log_rejection(
            trace,
            node="anti_slop_critic",
            reason=result.verdict,
            failed_metrics=event.failed_metrics,
            rejected_excerpt=event.rejected_excerpt,
            retry_count=total_retry,
        )
    else:
        log.append("[Critic] APPROVED")

    update: dict[str, Any] = {
        "last_critic_report": result.model_dump(),
        "critic_attempts": critic_attempts,
        "total_retry_count": total_retry,
        "rejection_history": rejection_history,
        "pipeline_log": log,
    }
    if result.decision == "APPROVED":
        update["final_elite_thread"] = state.get("current_tweets", [])

    return update
