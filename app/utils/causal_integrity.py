import re
from dataclasses import dataclass

from app.utils.anchor_preservation import evaluate_anchor_preservation
from app.utils.relational_consistency import (
    evaluate_open_question_preservation,
    evaluate_relational_consistency,
)


@dataclass
class CausalIntegrityResult:
    passed: bool
    reasons: list[str]
    metrics: dict


def evaluate_causal_integrity(
    tweets: list[str],
    distilled: dict,
) -> CausalIntegrityResult:
    """Combined relational + legacy anchor + open question checks."""
    causal = distilled.get("causal_anchors", [])
    legacy = distilled.get("insight_anchors", [])
    open_qs = distilled.get("open_questions", [])

    reasons: list[str] = []
    metrics: dict = {}

    if causal:
        rel = evaluate_relational_consistency(tweets, causal)
        metrics["relational_consistency"] = {
            "passed": rel.passed,
            "drift_events": rel.drift_events,
        }
        reasons.extend(rel.reasons)

    if legacy:
        leg = evaluate_anchor_preservation(tweets, legacy)
        metrics["legacy_anchors"] = {
            "passed": leg.passed,
            "ratio": leg.preservation_ratio,
        }
        reasons.extend(leg.reasons)

    oq_ok, oq_reasons = evaluate_open_question_preservation(tweets, open_qs)
    metrics["open_questions"] = {"passed": oq_ok}
    reasons.extend(oq_reasons)

    passed = len(reasons) == 0
    return CausalIntegrityResult(passed=passed, reasons=reasons, metrics=metrics)
