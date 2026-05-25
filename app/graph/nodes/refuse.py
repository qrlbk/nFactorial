from typing import Any

from app.config import get_settings
from app.graph.refusal_messages import (
    EPISTEMIC_REFUSAL,
    RETRY_REFUSAL,
    THESIS_CONFIDENCE_REFUSAL,
)
from app.i18n import localized_refusal, t
from app.i18n.evaluator_reasons import translate_evaluator_reason

_EARLY_REFUSALS = frozenset({EPISTEMIC_REFUSAL, THESIS_CONFIDENCE_REFUSAL})


def _build_retry_exhausted_reason(state: dict[str, Any]) -> str:
    locale = state.get("response_locale", "en")
    retries = int(state.get("total_retry_count", 0))
    history = state.get("rejection_history") or []
    last_failure = ""
    if history:
        last_failure = str(history[-1].get("reason", "")).split(";")[0].strip()

    parts = [localized_refusal(locale, "QUALITY")]
    if last_failure:
        parts.append(
            t(
                locale,
                "refusal.last_failure",
                reason=translate_evaluator_reason(last_failure, locale),
            )
        )
    parts.append(t(locale, "refusal.retries_exhausted", count=retries))
    return "\n".join(parts)


async def refuse_node(state: dict[str, Any]) -> dict[str, Any]:
    log = list(state.get("pipeline_log", []))
    log.append("[System] FAIL CLOSED")

    settings = get_settings()
    existing = state.get("refusal_reason")

    if existing in _EARLY_REFUSALS:
        reason = existing
    elif state.get("total_retry_count", 0) >= settings.max_critic_retries:
        reason = _build_retry_exhausted_reason(state)
    else:
        reason = existing or RETRY_REFUSAL

    log.append(reason)

    return {
        "refusal_reason": reason,
        "final_elite_thread": [],
        "pipeline_log": log,
    }
