from datetime import datetime, timezone
from typing import Any

from app.graph.output_profiles import get_profile
from app.schemas.trace import RejectionEvent
from app.services.tracing import log_rejection
from app.utils.causal_integrity import evaluate_causal_integrity
from app.utils.mechanistic_score import evaluate_mechanistic_density
from app.utils.semantic_density import evaluate_semantic_density
from app.utils.specificity_score import evaluate_specificity
from app.utils.text_metrics import evaluate_thesis_alignment, evaluate_thread_length

_PLATITUDE_PATTERNS = (
    "great point",
    "so true",
    "this is important",
    "well said",
    "couldn't agree more",
)


def _evaluate_qrt(tweets: list[str], thesis: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if len(tweets) != 1:
        reasons.append(f"QRT must be exactly 1 tweet, got {len(tweets)}")
    if tweets and len(tweets[0]) > 280:
        reasons.append("QRT exceeds 280 characters")
    if tweets:
        lower = tweets[0].lower()
        for pat in _PLATITUDE_PATTERNS:
            if pat in lower:
                reasons.append(f"QRT contains platitude pattern: {pat}")
        alignment = evaluate_thesis_alignment(
            tweets,
            defended_claim=thesis.get("defended_claim", ""),
            attacked_consensus=thesis.get("attacked_consensus", ""),
        )
        if not alignment.passed:
            reasons.extend(alignment.reasons)
    return len(reasons) == 0, reasons


def _evaluate_essay(sections: list[str], profile) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    text = "\n\n".join(sections)
    word_count = len(text.split())
    if len(sections) < profile.min_items:
        reasons.append(f"Essay has {len(sections)} sections, minimum is {profile.min_items}")
    if profile.min_words and word_count < profile.min_words:
        reasons.append(f"Essay has {word_count} words, minimum is {profile.min_words}")
    semantic = evaluate_semantic_density(text)
    if not semantic.passed:
        reasons.extend(semantic.reasons)
    return len(reasons) == 0, reasons


async def deterministic_evaluators_node(
    state: dict[str, Any],
    *,
    trace: Any = None,
) -> dict[str, Any]:
    output_type = state.get("output_type", "thread")
    profile = get_profile(output_type)
    tweets = state.get("current_tweets", [])
    thread_text = "\n".join(tweets) if tweets else state.get("current_draft", "")
    thesis = state.get("thesis_position") or {}
    anchors = state.get("distilled_context", {})
    output_language = state.get("output_language", "en")

    if output_type == "quote_retweet":
        all_passed, reasons = _evaluate_qrt(tweets, thesis)
        failed_metrics = {"qrt": {"passed": all_passed, "reasons": reasons}}
    elif output_type in ("essay", "article"):
        sections = state.get("essay_sections") or tweets
        all_passed, reasons = _evaluate_essay(sections, profile)
        failed_metrics = {"essay": {"passed": all_passed, "reasons": reasons}}
    else:
        causal_anchors = anchors.get("causal_anchors") or []
        anchor_values: list[str] = []
        for anchor in causal_anchors:
            for key in ("value", "metric", "subject", "comparison_target"):
                val = anchor.get(key)
                if val:
                    anchor_values.append(str(val))

        semantic = evaluate_semantic_density(thread_text)
        mechanistic = evaluate_mechanistic_density(thread_text, output_language=output_language)
        alignment = evaluate_thesis_alignment(
            tweets,
            defended_claim=thesis.get("defended_claim", ""),
            attacked_consensus=thesis.get("attacked_consensus", ""),
            output_language=output_language,
            causal_anchors=causal_anchors,
        )
        length = evaluate_thread_length(
            tweets,
            thread_min=profile.min_items,
            thread_max=profile.max_items,
            max_chars=profile.max_chars_per_item,
        )
        specificity = evaluate_specificity(
            thread_text,
            anchor_values=anchor_values,
            output_language=output_language,
        )
        causal = evaluate_causal_integrity(tweets, anchors)

        all_passed = (
            semantic.passed
            and mechanistic.passed
            and alignment.passed
            and length.passed
            and specificity.passed
            and causal.passed
        )
        reasons = (
            semantic.reasons
            + mechanistic.reasons
            + alignment.reasons
            + length.reasons
            + specificity.reasons
            + causal.reasons
        )
        failed_metrics = {
            "semantic": {"passed": semantic.passed, "reasons": semantic.reasons},
            "mechanistic": {"passed": mechanistic.passed, "reasons": mechanistic.reasons},
            "thesis_alignment": {"passed": alignment.passed, "reasons": alignment.reasons},
            "thread_length": {"passed": length.passed, "reasons": length.reasons},
            "specificity": {"passed": specificity.passed, "reasons": specificity.reasons},
            "causal_integrity": {"passed": causal.passed, "reasons": causal.reasons},
        }

    log = list(state.get("pipeline_log", []))
    rejection_history = list(state.get("rejection_history", []))
    total_retry = state.get("total_retry_count", 0)

    if all_passed:
        log.append("[Evaluators] PASSED")
        return {"eval_passed": True, "pipeline_log": log}

    total_retry += 1
    event = RejectionEvent(
        node="deterministic_evaluators",
        timestamp=datetime.now(timezone.utc),
        reason="; ".join(reasons),
        failed_metrics=failed_metrics,
        rejected_excerpt=thread_text[:500],
    )
    rejection_history.append(event.model_dump(mode="json"))
    log.append("[Evaluators] REJECTED")
    log.append("Reason:")
    for r in reasons:
        log.append(f"- {r}")

    log_rejection(
        trace,
        node="deterministic_evaluators",
        reason=event.reason,
        failed_metrics=failed_metrics,
        rejected_excerpt=event.rejected_excerpt,
        retry_count=total_retry,
    )

    return {
        "eval_passed": False,
        "rejection_history": rejection_history,
        "total_retry_count": total_retry,
        "pipeline_log": log,
    }
