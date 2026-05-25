import re
from dataclasses import dataclass

NAMED_TECH_PATTERNS = [
    r"\bRAG\b",
    r"\bLLM\b",
    r"\bLLMs\b",
    r"\bGPU\b",
    r"\bCUDA\b",
    r"\bHBM\b",
    r"\bAPI\b",
    r"\bMoE\b",
    r"\bRLHF\b",
    r"\bNVIDIA\b",
    r"\bPinecone\b",
    r"\bGPT\b",
    r"\bOpenAI\b",
    r"\bHN\b",
    r"\bMoore",
    r"\bvector\s+db",
    r"\bembedding",
    r"\brerank",
    r"\bfine-?tun",
    r"\bcontext\s+window",
    r"\btoken",
    r"\binference",
    r"\bdistill",
]

OPERATIONAL_NOUNS = [
    "latency",
    "throughput",
    "index",
    "pipeline",
    "margin",
    "cost",
    "pricing",
    "switching",
    "constraint",
    "bandwidth",
    "incentive",
    "subsidy",
    "deploy",
    "chunk",
    "query",
    "hallucination",
    "retrieval",
    "re-index",
    "inference",
    "compute",
    "parameter",
    "supply",
]

NUMBER_PATTERNS = [
    r"\d+[kKmM]?",
    r"\d+%",
    r"\d+\.\d+",
    r"\d+\s*x",
    r"\d+x",
    r"\d+\s*(docs|weeks|months|years|ms|s|queries|tweets|нед|недель|док|документов|запросов|апта|апта)\b",
]

OPERATIONAL_NOUNS_I18N: dict[str, list[str]] = {
    "en": OPERATIONAL_NOUNS,
    "ru": [
        "латентность",
        "стоимость",
        "затрат",
        "маржа",
        "индекс",
        "индексация",
        "запрос",
        "галлюцина",
        "retrieval",
        "embedding",
        "rerank",
        "pipeline",
        "latency",
        "cost",
        "pricing",
        "margin",
        "inference",
        "compute",
        *OPERATIONAL_NOUNS,
    ],
    "kk": [
        "latency",
        "cost",
        "retrieval",
        "embedding",
        "pipeline",
        "margin",
        "pricing",
        "index",
        "query",
        "inference",
        *OPERATIONAL_NOUNS,
    ],
}

MEASURABLE_PATTERNS_I18N: dict[str, list[str]] = {
    "en": [
        r"\b(increased|decreased|reduced|faster|slower|more than|less than|up|down|went up|went down)\b",
    ],
    "ru": [
        r"\b(увеличил|снизил|вырос|упал|быстрее|медленнее|больше|меньше|up|down)\b",
    ],
    "kk": [
        r"\b(өсті|төмен|жоғары|аз|up|down)\b",
    ],
}

ABSTRACT_PATTERNS_I18N: dict[str, list[str]] = {
    "en": [r"\b(incentives|landscape|transform|future|possibilities|leaders|innovation)\b"],
    "ru": [r"\b(инновац|лидер|будущ|трансформ|ландшафт|возможност)\w*\b"],
    "kk": [r"\b(innovation|leader|future|transform)\w*\b"],
}


def _value_in_text(value: str, text: str) -> bool:
    token = str(value).strip().lower()
    lower = text.lower()
    if len(token) >= 2 and token in lower:
        return True
    for num in re.findall(r"\d+[kKmM%x]?", token):
        if num in lower:
            return True
    for word in re.findall(r"[\w]{4,}", token, flags=re.UNICODE):
        if word in lower:
            return True
    return False


@dataclass
class SpecificityResult:
    passed: bool
    score: float
    reasons: list[str]
    metrics: dict


def _count_numbers(text: str) -> int:
    hits: set[str] = set()
    for pattern in NUMBER_PATTERNS:
        for match in re.findall(pattern, text, re.I):
            hits.add(match.lower())
    return len(hits)


def evaluate_specificity(
    text: str,
    *,
    anchor_values: list[str] | None = None,
    output_language: str = "en",
) -> SpecificityResult:
    from app.config import get_settings

    settings = get_settings()
    lang = output_language if output_language in OPERATIONAL_NOUNS_I18N else "en"
    lower = text.lower()

    numbers = _count_numbers(text)
    named_tech = sum(1 for p in NAMED_TECH_PATTERNS if re.search(p, text, re.I))
    operational = sum(1 for n in OPERATIONAL_NOUNS_I18N[lang] if n in lower)
    measurable = 0
    for pattern in MEASURABLE_PATTERNS_I18N.get(lang, MEASURABLE_PATTERNS_I18N["en"]):
        measurable += len(re.findall(pattern, lower))
    abstract_only = 0
    for pattern in ABSTRACT_PATTERNS_I18N.get(lang, ABSTRACT_PATTERNS_I18N["en"]):
        abstract_only += len(re.findall(pattern, lower))

    anchor_hits = 0
    if anchor_values:
        for value in anchor_values:
            if _value_in_text(value, text):
                anchor_hits += 1

    raw = (
        min(numbers, 4) * 0.12
        + min(named_tech, 4) * 0.10
        + min(operational, 6) * 0.06
        + min(measurable, 3) * 0.05
        + min(anchor_hits, 4) * 0.08
        - max(0, abstract_only - 3) * 0.04
    )
    score = round(min(1.0, max(0.0, raw)), 3)

    concrete_pass = (
        numbers >= 2 and (named_tech >= 1 or operational >= 3)
    ) or (
        numbers >= 2 and anchor_hits >= 2
    ) or (
        numbers >= 1 and named_tech >= 2 and operational >= 2
    )
    passed = score >= settings.min_specificity_score or concrete_pass

    reasons: list[str] = []
    if not passed:
        reasons.append(
            f"Specificity score {score} below {settings.min_specificity_score} "
            "(need numbers, named systems, or operational nouns)"
        )

    return SpecificityResult(
        passed=passed,
        score=score,
        reasons=reasons,
        metrics={
            "numbers": numbers,
            "named_technologies": named_tech,
            "operational_nouns": operational,
            "measurable_claims": measurable,
            "abstract_hits": abstract_only,
            "anchor_hits": anchor_hits,
            "concrete_pass": concrete_pass,
        },
    )
