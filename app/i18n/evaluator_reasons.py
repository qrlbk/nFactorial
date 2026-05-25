from __future__ import annotations

import re

from app.i18n import t

_PATTERNS: list[tuple[str, str]] = [
    (r"Mechanism layers (\d+) below minimum (\d+)", "evaluator.mechanism_layers"),
    (r"Defended claim overlap ([\d.]+) below ([\d.]+)", "evaluator.defended_overlap"),
    (
        r"Specificity score ([\d.]+) below ([\d.]+)(?: \(need numbers, named systems, or operational nouns\))?",
        "evaluator.specificity",
    ),
    (
        r"Relation drift tweet (\d+): '([^']+)' \(([^)]+)\) attributed near '([^']+)' but subject '([^']+)' missing",
        "evaluator.relation_drift_comparison",
    ),
    (
        r"Relation drift tweet (\d+): '([^']+)' used without anchor subject '([^']+)'",
        "evaluator.relation_drift_subject",
    ),
    (r"Thread has (\d+) tweets, minimum is (\d+)", "evaluator.thread_min"),
    (r"Thread has (\d+) tweets, maximum is (\d+)", "evaluator.thread_max"),
    (r"Tweet (\d+) exceeds (\d+) characters", "evaluator.tweet_chars"),
    (r"Abstract noun density ([\d.]+) exceeds ([\d.]+)", "evaluator.abstract_density"),
]


def _translate_part(part: str, locale: str) -> str:
    for pattern, key in _PATTERNS:
        m = re.fullmatch(pattern, part.strip())
        if not m:
            continue
        groups = m.groups()
        if key == "evaluator.mechanism_layers":
            return t(locale, key, layers=groups[0], minimum=groups[1])
        if key == "evaluator.defended_overlap":
            return t(locale, key, overlap=groups[0], minimum=groups[1])
        if key == "evaluator.specificity":
            return t(locale, key, score=groups[0], minimum=groups[1])
        if key == "evaluator.relation_drift_comparison":
            return t(
                locale,
                key,
                tweet=groups[0],
                value=groups[1],
                metric=groups[2],
                comparison=groups[3],
                subject=groups[4],
            )
        if key == "evaluator.relation_drift_subject":
            return t(locale, key, tweet=groups[0], value=groups[1], subject=groups[2])
        if key == "evaluator.thread_min":
            return t(locale, key, count=groups[0], minimum=groups[1])
        if key == "evaluator.thread_max":
            return t(locale, key, count=groups[0], maximum=groups[1])
        if key == "evaluator.tweet_chars":
            return t(locale, key, index=groups[0], maximum=groups[1])
        if key == "evaluator.abstract_density":
            return t(locale, key, density=groups[0], maximum=groups[1])
    return part.strip()


def translate_evaluator_reason(reason: str, locale: str | None) -> str:
    if not reason or not locale or locale == "en":
        return reason
    parts = [p.strip() for p in reason.split(";") if p.strip()]
    return "; ".join(_translate_part(part, locale) for part in parts)


def localize_rejection_history(history: list[dict], locale: str | None) -> list[dict]:
    if not locale or locale == "en":
        return history
    localized: list[dict] = []
    for event in history:
        item = dict(event)
        if item.get("reason"):
            item["reason"] = translate_evaluator_reason(str(item["reason"]), locale)
        localized.append(item)
    return localized


def localize_pipeline_timeline(timeline: list[dict], locale: str | None) -> list[dict]:
    if not locale or locale == "en":
        return timeline
    localized: list[dict] = []
    for row in timeline:
        item = dict(row)
        detail = str(item.get("detail", ""))
        if item.get("node") == "refuse":
            item["detail"] = t(locale, "pipeline.detail.quality_failed")
        elif detail:
            translated = translate_evaluator_reason(detail, locale)
            item["detail"] = translated[:160] + ("…" if len(translated) > 160 else "")
        localized.append(item)
    return localized
