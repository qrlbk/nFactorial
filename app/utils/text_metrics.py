import re
from dataclasses import dataclass

from app.config import get_settings


@dataclass
class ThreadLengthResult:
    passed: bool
    tweet_count: int
    reasons: list[str]
    char_violations: list[int]


@dataclass
class ThesisAlignmentResult:
    passed: bool
    defended_overlap: float
    consensus_dominance: bool
    reasons: list[str]


def _significant_tokens(text: str) -> set[str]:
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "to", "of",
        "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "that", "this", "it", "its", "and", "or", "but", "not", "no", "so",
        "if", "than", "then", "they", "them", "their", "we", "our", "you",
    }
    tokens = re.findall(r"[\w]{3,}", text.lower(), flags=re.UNICODE)
    return {tok for tok in tokens if tok not in stop and not tok.isdigit()}


def _field_in_thread(raw: str, thread: str) -> bool:
    token = str(raw).strip().lower()
    lower = thread.lower()
    if len(token) >= 2 and token in lower:
        return True
    for num in re.findall(r"\d+[kKmM%x]?", token):
        if num in lower:
            return True
    for word in re.findall(r"[\w]{4,}", token, flags=re.UNICODE):
        if word in lower:
            return True
    return False


def _anchor_presence_score(tweets: list[str], causal_anchors: list[dict]) -> float:
    if not causal_anchors:
        return 0.0
    thread = " ".join(tweets).lower()
    hits = 0
    checks = 0
    for anchor in causal_anchors:
        for field in ("subject", "metric", "value", "comparison_target"):
            raw = str(anchor.get(field, "")).strip()
            if len(raw) < 2:
                continue
            checks += 1
            if _field_in_thread(raw, thread):
                hits += 1
    if checks == 0:
        return 0.0
    return hits / checks


def evaluate_thread_length(
    tweets: list[str],
    *,
    thread_min: int | None = None,
    thread_max: int | None = None,
    max_chars: int | None = None,
) -> ThreadLengthResult:
    settings = get_settings()
    thread_min = thread_min or settings.thread_min
    thread_max = thread_max or settings.thread_max
    max_chars = max_chars or settings.tweet_max_chars

    reasons: list[str] = []
    count = len(tweets)
    if count < thread_min:
        reasons.append(f"Thread has {count} tweets, minimum is {thread_min}")
    if count > thread_max:
        reasons.append(f"Thread has {count} tweets, maximum is {thread_max}")

    char_violations = []
    for i, tweet in enumerate(tweets):
        if len(tweet) > max_chars:
            char_violations.append(i)
            reasons.append(f"Tweet {i + 1} exceeds {max_chars} characters")

    passed = len(reasons) == 0
    return ThreadLengthResult(
        passed=passed,
        tweet_count=count,
        reasons=reasons,
        char_violations=char_violations,
    )


def evaluate_thesis_alignment(
    tweets: list[str],
    defended_claim: str,
    attacked_consensus: str,
    *,
    min_overlap_ratio: float = 0.15,
    output_language: str = "en",
    causal_anchors: list[dict] | None = None,
) -> ThesisAlignmentResult:
    thread_text = " ".join(tweets)
    defended_tokens = _significant_tokens(defended_claim)
    consensus_tokens = _significant_tokens(attacked_consensus)
    thread_tokens = _significant_tokens(thread_text)

    if not defended_tokens:
        return ThesisAlignmentResult(
            passed=False,
            defended_overlap=0.0,
            consensus_dominance=False,
            reasons=["Defended claim has no significant tokens"],
        )

    overlap = len(defended_tokens & thread_tokens) / len(defended_tokens)
    if output_language != "en" and causal_anchors:
        anchor_score = _anchor_presence_score(tweets, causal_anchors)
        overlap = max(overlap, anchor_score)
    consensus_overlap = (
        len(consensus_tokens & thread_tokens) / len(consensus_tokens)
        if consensus_tokens
        else 0.0
    )
    consensus_dominance = consensus_overlap > overlap and consensus_overlap >= min_overlap_ratio

    reasons: list[str] = []
    if overlap < min_overlap_ratio:
        reasons.append(
            f"Defended claim overlap {overlap:.2f} below {min_overlap_ratio}"
        )
    if consensus_dominance and overlap < min_overlap_ratio * 1.5:
        reasons.append("Consensus terms dominate without defended claim presence")

    passed = len(reasons) == 0
    return ThesisAlignmentResult(
        passed=passed,
        defended_overlap=overlap,
        consensus_dominance=consensus_dominance,
        reasons=reasons,
    )
