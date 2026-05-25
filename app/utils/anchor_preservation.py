import re
from dataclasses import dataclass


@dataclass
class AnchorPreservationResult:
    passed: bool
    preservation_ratio: float
    reasons: list[str]
    missing_anchors: list[str]


def _anchor_tokens(text: str) -> set[str]:
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "to", "of", "in", "for", "on", "with", "at",
        "by", "from", "as", "that", "this", "it", "and", "or", "but", "not",
    }
    tokens = re.findall(r"[a-zA-Z0-9]{3,}", text.lower())
    return {t for t in tokens if t not in stop}


def evaluate_anchor_preservation(
    tweets: list[str],
    anchors: list[dict],
) -> AnchorPreservationResult:
    from app.config import get_settings

    settings = get_settings()
    thread_text = " ".join(tweets)
    thread_tokens = _anchor_tokens(thread_text)

    must_preserve = [a for a in anchors if a.get("must_preserve", True)]
    if not must_preserve:
        return AnchorPreservationResult(
            passed=True,
            preservation_ratio=1.0,
            reasons=[],
            missing_anchors=[],
        )

    preserved = 0
    missing: list[str] = []
    for anchor in must_preserve:
        obs = anchor.get("exact_observation", "")
        anchor_tokens = _anchor_tokens(obs)
        if not anchor_tokens:
            continue
        overlap = len(anchor_tokens & thread_tokens) / len(anchor_tokens)
        # Also accept numeric substring preservation
        nums = re.findall(r"\d+", obs)
        num_preserved = all(n in thread_text for n in nums) if nums else False
        if overlap >= 0.35 or num_preserved:
            preserved += 1
        else:
            missing.append(obs[:80])

    ratio = preserved / len(must_preserve)
    reasons: list[str] = []
    if ratio < settings.min_anchor_preservation_ratio:
        reasons.append(
            f"Insight anchor preservation {ratio:.2f} below "
            f"{settings.min_anchor_preservation_ratio}"
        )

    passed = len(reasons) == 0
    return AnchorPreservationResult(
        passed=passed,
        preservation_ratio=round(ratio, 3),
        reasons=reasons,
        missing_anchors=missing,
    )
