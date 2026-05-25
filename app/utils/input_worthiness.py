import re
from dataclasses import dataclass

GENERIC_BUZZ_PHRASES = [
    "ai is transforming",
    "transforming everything",
    "future of work",
    "game-changer",
    "revolutionize",
    "huge opportunity",
    "excited about",
    "companies need to adopt",
    "adopt ai or die",
    "blockchain",
    "metaverse",
    "paradigm shift",
    "in today's world",
    "the possibilities ahead",
]

OPERATIONAL_MARKERS = [
    "latency",
    "cost",
    "tried",
    "tested",
    "we ",
    "our ",
    "pipeline",
    "index",
    "rerank",
    "embedding",
    "chunk",
    "docs",
    "weeks",
    "query",
    "infra",
    "ops",
    "benchmark",
    "a/b",
    "deploy",
    "production",
    "margin",
    "switching",
]

TENSION_MARKERS = [
    "counter",
    "but ",
    "however",
    "wrong",
    "actually",
    "nobody talks",
    "real issue",
    "misleading",
    "contradict",
    "falsif",
    "open question",
    "am i wrong",
]

STAKES_MARKERS = [
    "money",
    "cost",
    "margin",
    "moat",
    "vendor",
    "replace",
    "fail",
    "killed",
    "dominance",
    "subsidy",
    "pricing",
]


@dataclass
class InputWorthinessResult:
    passed: bool
    score: float
    reasons: list[str]
    metrics: dict


def _count_pattern_matches(text: str, patterns: list[str]) -> int:
    lower = text.lower()
    return sum(1 for p in patterns if p in lower)


def evaluate_input_worthiness(text: str) -> InputWorthinessResult:
    from app.config import get_settings

    settings = get_settings()
    lower = text.lower()
    words = re.findall(r"[a-zA-Z']+", lower)
    word_count = len(words)

    reasons: list[str] = []
    if word_count < 25:
        reasons.append(f"Input too short ({word_count} words, need ≥25)")

    numbers = len(re.findall(r"\d+", text))
    buzz_count = _count_pattern_matches(lower, GENERIC_BUZZ_PHRASES)
    operational = _count_pattern_matches(lower, OPERATIONAL_MARKERS)
    tension = _count_pattern_matches(lower, TENSION_MARKERS)
    stakes = _count_pattern_matches(lower, STAKES_MARKERS)

    signal_categories = sum(
        [
            numbers >= 1,
            operational >= 2,
            tension >= 1,
            stakes >= 1,
            word_count >= 60,
        ]
    )

    if signal_categories < 2:
        reasons.append(
            "Insufficient intellectual signals (need ≥2 of: numbers, operational detail, "
            "tension/contradiction, stakes, substantive length)"
        )

    if buzz_count >= 2 and operational < 2 and numbers == 0:
        reasons.append(
            f"Generic buzzword density ({buzz_count} phrases) without operational specificity"
        )

    if buzz_count >= 3 and signal_categories < 3:
        reasons.append("Input reads as hype-only; lacks falsifiable or operational material")

    # Score: weighted epistemic signals minus buzz penalty
    score = min(
        1.0,
        max(
            0.0,
            (signal_categories * 0.18)
            + (min(numbers, 3) * 0.08)
            + (min(operational, 5) * 0.06)
            + (min(tension, 3) * 0.05)
            - (buzz_count * 0.12),
        ),
    )

    passed = score >= settings.min_input_worthiness_score and len(reasons) == 0

    return InputWorthinessResult(
        passed=passed,
        score=round(score, 3),
        reasons=reasons,
        metrics={
            "word_count": word_count,
            "numbers": numbers,
            "operational_markers": operational,
            "tension_markers": tension,
            "stakes_markers": stakes,
            "buzz_phrases": buzz_count,
            "signal_categories": signal_categories,
        },
    )
