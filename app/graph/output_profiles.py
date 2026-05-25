from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OutputType = Literal["thread", "quote_retweet", "essay", "article"]


@dataclass(frozen=True)
class OutputProfile:
    output_type: OutputType
    min_items: int
    max_items: int
    max_chars_per_item: int
    min_words: int | None = None
    max_words: int | None = None
    require_thesis_alignment: bool = True
    require_mechanistic: bool = True
    require_causal_integrity: bool = True


PROFILES: dict[OutputType, OutputProfile] = {
    "thread": OutputProfile(
        output_type="thread",
        min_items=6,
        max_items=9,
        max_chars_per_item=280,
    ),
    "quote_retweet": OutputProfile(
        output_type="quote_retweet",
        min_items=1,
        max_items=1,
        max_chars_per_item=280,
        require_mechanistic=False,
    ),
    "essay": OutputProfile(
        output_type="essay",
        min_items=5,
        max_items=8,
        max_chars_per_item=4000,
        min_words=1500,
        max_words=4000,
    ),
    "article": OutputProfile(
        output_type="article",
        min_items=5,
        max_items=10,
        max_chars_per_item=5000,
        min_words=2000,
        max_words=5000,
    ),
}


def get_profile(output_type: str) -> OutputProfile:
    return PROFILES.get(output_type, PROFILES["thread"])  # type: ignore[arg-type]
