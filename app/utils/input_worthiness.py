import re
from dataclasses import dataclass

GENERIC_BUZZ_PHRASES_I18N: dict[str, list[str]] = {
    "en": [
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
    ],
    "ru": [
        "ии меняет всё",
        "трансформирует всё",
        "будущее работы",
        "прорыв",
        "революцион",
        "огромная возможность",
        "в восторге",
        "нужно внедрять",
        "блокчейн",
        "метавселен",
        "смена парадигм",
        "в современном мире",
        "возможности впереди",
        "game-changer",
        "paradigm shift",
    ],
    "kk": [
        "ai is transforming",
        "болашақ жұмыс",
        "революция",
        "үлкен мүмкіндік",
        "blockchain",
        "metaverse",
        "paradigm shift",
        "game-changer",
    ],
}

OPERATIONAL_MARKERS_I18N: dict[str, list[str]] = {
    "en": [
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
    ],
    "ru": [
        "латентность",
        "стоимость",
        "затрат",
        "попробовал",
        "тестировал",
        "мы ",
        "наш ",
        "пайплайн",
        "индекс",
        "rerank",
        "embedding",
        "чанк",
        "документ",
        "недель",
        "запрос",
        "инфра",
        "прод",
        "бенчмарк",
        "деплой",
        "маржа",
        "latency",
        "pipeline",
        "cost",
        "deploy",
        "production",
    ],
    "kk": [
        "латенттік",
        "құны",
        "біз ",
        "біздің ",
        "pipeline",
        "индекс",
        "embedding",
        "сұраныс",
        "апта",
        "deploy",
        "latency",
        "cost",
        "production",
        "margin",
    ],
}

TENSION_MARKERS_I18N: dict[str, list[str]] = {
    "en": [
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
    ],
    "ru": [
        "но ",
        "однако",
        "на самом деле",
        "ошиба",
        "никто не говорит",
        "реальная проблема",
        "вводит в заблуждение",
        "противореч",
        "опроверг",
        "открытый вопрос",
        "я не прав",
        "counter",
        "however",
    ],
    "kk": [
        "бірақ ",
        "алайда",
        "шын мәнінде",
        "қате",
        "ашық сұрақ",
        "but ",
        "however",
    ],
}

STAKES_MARKERS_I18N: dict[str, list[str]] = {
    "en": [
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
    ],
    "ru": [
        "деньги",
        "стоимость",
        "маржа",
        "moat",
        "вендор",
        "замен",
        "провал",
        "убил",
        "доминирован",
        "субсид",
        "ценообраз",
        "margin",
        "pricing",
    ],
    "kk": [
        "ақша",
        "құны",
        "маржа",
        "vendor",
        "fail",
        "pricing",
        "margin",
        "cost",
    ],
}


@dataclass
class InputWorthinessResult:
    passed: bool
    score: float
    reasons: list[str]
    metrics: dict


def _count_words(text: str) -> int:
    """Count words in Latin, Cyrillic, and other Unicode letters."""
    return len(re.findall(r"[\w']+", text, flags=re.UNICODE))


def _count_pattern_matches(text: str, patterns: list[str]) -> int:
    lower = text.lower()
    return sum(1 for p in patterns if p in lower)


def _resolve_language(text: str, output_language: str = "en") -> str:
    """Pick marker set from output_language; fall back to script detection."""
    lang = output_language if output_language in ("en", "ru", "kk") else "en"
    cyrillic = len(re.findall(r"[\u0400-\u04FF]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))
    if cyrillic >= 15 and cyrillic > latin:
        if lang == "en":
            return "ru"
    return lang


def evaluate_input_worthiness(
    text: str,
    *,
    output_language: str = "en",
) -> InputWorthinessResult:
    from app.config import get_settings

    settings = get_settings()
    lang = _resolve_language(text, output_language)
    lower = text.lower()
    word_count = _count_words(text)

    buzz = GENERIC_BUZZ_PHRASES_I18N.get(lang, GENERIC_BUZZ_PHRASES_I18N["en"])
    operational = OPERATIONAL_MARKERS_I18N.get(lang, OPERATIONAL_MARKERS_I18N["en"])
    tension = TENSION_MARKERS_I18N.get(lang, TENSION_MARKERS_I18N["en"])
    stakes = STAKES_MARKERS_I18N.get(lang, STAKES_MARKERS_I18N["en"])

    reasons: list[str] = []
    if word_count < 25:
        reasons.append(f"Input too short ({word_count} words, need ≥25)")

    numbers = len(re.findall(r"\d+", text))
    buzz_count = _count_pattern_matches(lower, buzz)
    operational_hits = _count_pattern_matches(lower, operational)
    tension_hits = _count_pattern_matches(lower, tension)
    stakes_hits = _count_pattern_matches(lower, stakes)

    signal_categories = sum(
        [
            numbers >= 1,
            operational_hits >= 2,
            tension_hits >= 1,
            stakes_hits >= 1,
            word_count >= 60,
        ]
    )

    if signal_categories < 2:
        reasons.append(
            "Insufficient intellectual signals (need ≥2 of: numbers, operational detail, "
            "tension/contradiction, stakes, substantive length)"
        )

    if buzz_count >= 2 and operational_hits < 2 and numbers == 0:
        reasons.append(
            f"Generic buzzword density ({buzz_count} phrases) without operational specificity"
        )

    if buzz_count >= 3 and signal_categories < 3:
        reasons.append("Input reads as hype-only; lacks falsifiable or operational material")

    score = min(
        1.0,
        max(
            0.0,
            (signal_categories * 0.18)
            + (min(numbers, 3) * 0.08)
            + (min(operational_hits, 5) * 0.06)
            + (min(tension_hits, 3) * 0.05)
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
            "operational_markers": operational_hits,
            "tension_markers": tension_hits,
            "stakes_markers": stakes_hits,
            "buzz_phrases": buzz_count,
            "signal_categories": signal_categories,
            "language": lang,
        },
    )
