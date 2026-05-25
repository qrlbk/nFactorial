import re
from dataclasses import dataclass

CAUSAL_MARKERS = [
    "because",
    "bc",
    "so",
    "since",
    "therefore",
    "thus",
    "drives",
    "causes",
    "forces",
    "leads to",
    "results in",
    "compels",
    "—",
    "matched by",
    "comes from",
]

CAUSAL_MARKERS_I18N: dict[str, list[str]] = {
    "en": CAUSAL_MARKERS,
    "ru": [
        "потому что",
        "поэтому",
        "так как",
        "так что",
        "из-за",
        "следовательно",
        "значит",
        "because",
        "therefore",
        "bc",
    ],
    "kk": ["өйткені", "сондықтан", "себебі", "because", "therefore", "bc"],
}

MECHANISM_MARKERS = [
    "incentive",
    "incentives",
    "constraint",
    "constraints",
    "tradeoff",
    "trade-off",
    "marginal",
    "cost",
    "latency",
    "retrieval",
    "embedding",
    "rerank",
    "pipeline",
    "supply",
    "demand",
    "pricing",
    "adoption",
    "switching cost",
    "moat",
    "unit economics",
    "feedback loop",
    "coordination",
    "principal-agent",
    "inference",
    "gpu",
    "cuda",
    "nvidia",
    "parameter",
    "compute",
    "transistor",
    "distillation",
    "marginal cost",
]

MECHANISM_MARKERS_I18N: dict[str, list[str]] = {
    "en": MECHANISM_MARKERS,
    "ru": [
        "стоимость",
        "затрат",
        "латентность",
        "маржа",
        "retrieval",
        "embedding",
        "rerank",
        "индекс",
        "pipeline",
        "cost",
        "latency",
        "pricing",
        "moat",
        *MECHANISM_MARKERS,
    ],
    "kk": [
        "құны",
        "latency",
        "cost",
        "retrieval",
        "embedding",
        "pricing",
        "margin",
        "pipeline",
        "index",
        *MECHANISM_MARKERS,
    ],
}


@dataclass
class MechanisticDensityResult:
    passed: bool
    mechanism_layers: int
    causal_sentence_count: int
    reasons: list[str]


def _split_sentences(text: str) -> list[str]:
    """Split on tweet boundaries (newlines) and sentence-ending punctuation."""
    parts: list[str] = []
    for chunk in re.split(r"[\n]+", text):
        for sentence in re.split(r"[.!?]+", chunk):
            s = sentence.strip()
            if s:
                parts.append(s)
    return parts


def _sentence_has_marker(sentence: str, markers: list[str]) -> bool:
    lower = sentence.lower()
    return any(m in lower for m in markers)


def evaluate_mechanistic_density(
    text: str,
    *,
    min_mechanism_layers: int = 2,
    output_language: str = "en",
) -> MechanisticDensityResult:
    lang = output_language if output_language in CAUSAL_MARKERS_I18N else "en"
    causal_markers = CAUSAL_MARKERS_I18N[lang]
    mechanism_markers = MECHANISM_MARKERS_I18N[lang]
    sentences = _split_sentences(text)
    layers = 0
    causal_count = 0

    for sentence in sentences:
        has_causal = _sentence_has_marker(sentence, causal_markers)
        has_mechanism = _sentence_has_marker(sentence, mechanism_markers)
        has_number = bool(re.search(r"\d|[0-9]+x|10x|near-zero", sentence, re.I))
        if has_causal:
            causal_count += 1
        if has_causal and has_mechanism:
            layers += 1
        elif has_mechanism and has_number and len(sentence.split()) >= 5:
            layers += 1
        elif has_mechanism and len(sentence.split()) >= 8:
            layers += 1

    reasons: list[str] = []
    if layers < min_mechanism_layers:
        reasons.append(
            f"Mechanism layers {layers} below minimum {min_mechanism_layers}"
        )

    passed = len(reasons) == 0
    return MechanisticDensityResult(
        passed=passed,
        mechanism_layers=layers,
        causal_sentence_count=causal_count,
        reasons=reasons,
    )
