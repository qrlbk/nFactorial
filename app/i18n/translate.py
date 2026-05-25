from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

LOCALES_DIR = Path(__file__).resolve().parent / "locales"
SUPPORTED_LOCALES = frozenset({"en", "ru", "kk"})
DEFAULT_LOCALE = "en"

REFUSAL_KEYS = {
    "EPISTEMIC": "refusal.epistemic",
    "THESIS": "refusal.thesis",
    "RETRY": "refusal.retry",
    "QUALITY": "refusal.quality_exhausted",
}


@lru_cache(maxsize=8)
def _load_locale(locale: str) -> dict[str, Any]:
    path = LOCALES_DIR / f"{locale}.json"
    if not path.exists():
        path = LOCALES_DIR / f"{DEFAULT_LOCALE}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_locale(locale: str | None) -> str:
    if not locale:
        return DEFAULT_LOCALE
    code = locale.lower().split(",")[0].split("-")[0].strip()
    if code in SUPPORTED_LOCALES:
        return code
    return DEFAULT_LOCALE


def _lookup(data: dict[str, Any], key: str) -> str | None:
    current: Any = data
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current if isinstance(current, str) else None


def t(locale: str | None, key: str, **kwargs: Any) -> str:
    loc = normalize_locale(locale)
    text = _lookup(_load_locale(loc), key) or _lookup(_load_locale(DEFAULT_LOCALE), key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def output_language_name(code: str) -> str:
    loc = normalize_locale(code)
    return t("en", f"language.{loc}")


def localized_refusal(locale: str | None, kind: str) -> str:
    key = REFUSAL_KEYS.get(kind.upper(), REFUSAL_KEYS["RETRY"])
    return t(locale, key)


def translate_refusal_if_known(locale: str | None, reason: str | None) -> str | None:
    if not reason:
        return reason
    from app.graph import refusal_messages as rm

    mapping = {
        rm.EPISTEMIC_REFUSAL: localized_refusal(locale, "EPISTEMIC"),
        rm.THESIS_CONFIDENCE_REFUSAL: localized_refusal(locale, "THESIS"),
        rm.RETRY_REFUSAL: localized_refusal(locale, "RETRY"),
    }
    if reason in mapping:
        return mapping[reason]

    if reason.startswith(rm.RETRY_REFUSAL):
        base = mapping[rm.RETRY_REFUSAL]
        suffix = reason[len(rm.RETRY_REFUSAL) :].strip()
        match = re.search(r"after (\d+) attempts?", suffix, re.IGNORECASE)
        if match and base:
            return f"{base}\n{t(locale, 'refusal.retries_exhausted', count=match.group(1))}"
        return base

    return reason
