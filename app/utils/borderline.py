import re
from dataclasses import dataclass

BORDERLINE_MARKERS = [
    "kinda obvious",
    "probably obvious",
    "not sure this matters",
    "maybe not interesting",
    "not sure if this is",
    "worth writing",
    "kinda obvious?",
    "obvious tho",
    "not sure this is a thread",
]


@dataclass
class BorderlineResult:
    is_borderline: bool
    markers_found: list[str]
    critic_strictness_boost: float


def detect_borderline_input(text: str, *, boost: float = 0.15) -> BorderlineResult:
    lower = text.lower()
    found = [m for m in BORDERLINE_MARKERS if m in lower]
    return BorderlineResult(
        is_borderline=len(found) > 0,
        markers_found=found,
        critic_strictness_boost=boost if found else 0.0,
    )
