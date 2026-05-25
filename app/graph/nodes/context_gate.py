from datetime import datetime, timezone
from typing import Any

from app.graph.refusal_messages import EPISTEMIC_REFUSAL
from app.schemas.trace import RejectionEvent
from app.services.tracing import log_rejection
from app.config import get_settings
from app.utils.borderline import detect_borderline_input
from app.utils.input_worthiness import evaluate_input_worthiness


async def context_qualification_gate_node(
    state: dict[str, Any],
    *,
    trace: Any = None,
) -> dict[str, Any]:
    """Deterministic epistemic gate — runs before thesis to block empty cognition."""
    raw = state.get("raw_context", "")
    result = evaluate_input_worthiness(raw)
    borderline = detect_borderline_input(raw)

    log = list(state.get("pipeline_log", []))
    log.append("[Context Gate] DONE")

    if result.passed:
        log.append(f"[Context Gate] QUALIFIED (score={result.score})")
        if borderline.is_borderline:
            log.append("[Context Gate] BORDERLINE — elevated critic strictness")
            for m in borderline.markers_found:
                log.append(f"- self-doubt marker: {m}")
        return {
            "context_qualified": True,
            "input_worthiness_score": result.score,
            "borderline_input": borderline.is_borderline,
            "critic_strictness_boost": borderline.critic_strictness_boost,
            "pipeline_log": log,
        }

    log.append("[Context Gate] REFUSED")
    log.append("Reason:")
    for r in result.reasons:
        log.append(f"- {r}")

    rejection_history = list(state.get("rejection_history", []))
    event = RejectionEvent(
        node="context_qualification_gate",
        timestamp=datetime.now(timezone.utc),
        reason="; ".join(result.reasons) or "Insufficient epistemic density",
        failed_metrics=result.metrics,
        rejected_excerpt=raw[:300],
    )
    rejection_history.append(event.model_dump(mode="json"))

    log_rejection(
        trace,
        node="context_qualification_gate",
        reason=event.reason,
        failed_metrics={**result.metrics, "worthiness_score": result.score},
        rejected_excerpt=event.rejected_excerpt,
        retry_count=0,
    )

    return {
        "context_qualified": False,
        "refusal_reason": EPISTEMIC_REFUSAL,
        "rejection_history": rejection_history,
        "pipeline_log": log,
    }
