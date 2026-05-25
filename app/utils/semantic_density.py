import re
from dataclasses import dataclass

ABSTRACT_NOUNS = {
    "innovation",
    "landscape",
    "paradigm",
    "ecosystem",
    "synergy",
    "transformation",
    "disruption",
    "leverage",
    "scalability",
    "framework",
    "holistic",
    "dynamic",
    "nuance",
    "complexity",
    "intersection",
    "narrative",
    "trajectory",
    "implications",
    "significance",
    "potential",
}

HEDGE_PHRASES = [
    "might",
    "could",
    "perhaps",
    "somewhat",
    "relatively",
    "arguably",
    "potentially",
    "in some ways",
    "to some extent",
    "it seems",
    "appears to",
]

FLUFF_INDICATORS = [
    "it's important to note",
    "it is important to note",
    "in today's world",
    "at the end of the day",
    "moving forward",
    "going forward",
    "the reality is",
    "needless to say",
    "bears mentioning",
    "food for thought",
]


@dataclass
class SemanticDensityResult:
    passed: bool
    abstract_noun_density: float
    hedge_count: int
    fluff_count: int
    reasons: list[str]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def evaluate_semantic_density(
    text: str,
    *,
    max_abstract_density: float = 0.08,
    max_hedge_count: int = 2,
    max_fluff_count: int = 0,
) -> SemanticDensityResult:
    tokens = _tokenize(text)
    word_count = max(len(tokens), 1)
    abstract_count = sum(1 for t in tokens if t in ABSTRACT_NOUNS)
    density = abstract_count / word_count

    lower = text.lower()
    hedge_count = sum(lower.count(h) for h in HEDGE_PHRASES)
    fluff_count = sum(1 for f in FLUFF_INDICATORS if f in lower)

    reasons: list[str] = []
    if density > max_abstract_density:
        reasons.append(
            f"Abstract noun density {density:.3f} exceeds {max_abstract_density}"
        )
    if hedge_count > max_hedge_count:
        reasons.append(f"Hedge phrase count {hedge_count} exceeds {max_hedge_count}")
    if fluff_count > max_fluff_count:
        reasons.append(f"Fluff indicators detected: {fluff_count}")

    passed = len(reasons) == 0
    return SemanticDensityResult(
        passed=passed,
        abstract_noun_density=density,
        hedge_count=hedge_count,
        fluff_count=fluff_count,
        reasons=reasons,
    )
