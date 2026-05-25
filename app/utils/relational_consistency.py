import re
from dataclasses import dataclass

# Token aliases so subject presence survives paraphrase (capability → parameter, etc.)
_SUBJECT_ALIASES: dict[str, set[str]] = {
    "model": {"model", "models", "llm", "llms", "gpt", "moore"},
    "capability": {"capability", "capabilities", "parameter", "parameters", "compute", "inference"},
    "increase": {"increase", "increased", "growth", "rose", "expand", "expansion", "10x", "matched"},
    "cost": {"cost", "costs", "pricing", "price", "prices", "margin", "marginal"},
    "latency": {"latency", "delay", "delays", "slow", "slower", "ms", "throughput"},
    "inference": {"inference", "infer", "decode", "token", "tokens", "gpu", "cuda"},
    "nvidia": {"nvidia", "cuda", "gpu", "gpus", "hbm"},
    "efficiency": {"efficiency", "efficient", "distill", "distillation", "quantization", "moe"},
}


@dataclass
class RelationalConsistencyResult:
    passed: bool
    reasons: list[str]
    drift_events: list[dict]


def _subject_tokens(subject: str) -> set[str]:
    stop = {"the", "full", "context", "pipeline", "path", "via", "with"}
    tokens = re.findall(r"[a-zA-Z0-9]{2,}", subject.lower())
    return {t for t in tokens if t not in stop and len(t) > 2}


def _comparison_tokens(comparison_target: str) -> set[str]:
    if not comparison_target:
        return set()
    tokens = re.findall(r"[a-zA-Z0-9]{2,}", comparison_target.lower())
    return {t for t in tokens if len(t) > 2}


def _tweet_mentions_value(tweet: str, value: str, metric: str) -> bool:
    if value and value.lower() in tweet.lower():
        return True
    if metric and metric.lower() in tweet.lower():
        return True
    return False


def _token_in_text(token: str, text: str) -> bool:
    lower = text.lower()
    if token in lower:
        return True
    if token.endswith("s") and len(token) > 3 and token[:-1] in lower:
        return True
    if not token.endswith("s") and f"{token}s" in lower:
        return True
    return False


def _subject_present(tweet: str, subject_tokens: set[str]) -> bool:
    lower = tweet.lower()
    if not subject_tokens:
        return True
    hits = sum(1 for tok in subject_tokens if _token_in_text(tok, lower))
    return hits >= max(1, len(subject_tokens) // 3)


def evaluate_relational_consistency(
    tweets: list[str],
    causal_anchors: list[dict],
) -> RelationalConsistencyResult:
    """
    Hybrid relational integrity check (regex/token — no LLM).

    Detects when metric/value from anchor is attributed to wrong subject
    (e.g. RAG gets 8s latency that belongs to full-context GPT-4o).
    """
    reasons: list[str] = []
    drift_events: list[dict] = []

    for anchor in causal_anchors:
        subject = anchor.get("subject", "")
        metric = anchor.get("metric", "")
        value = str(anchor.get("value", ""))
        comparison = anchor.get("comparison_target", "")
        relationship = anchor.get("relationship", "")

        subject_tokens = _subject_tokens(subject)
        comp_tokens = _comparison_tokens(comparison)

        for i, tweet in enumerate(tweets):
            if not _tweet_mentions_value(tweet, value, metric):
                continue

            lower = tweet.lower()
            subj_ok = _subject_present(tweet, subject_tokens)

            # Drift: value/metric in tweet, subject absent, comparison entity present
            comp_in_tweet = any(t in lower for t in comp_tokens if len(t) > 2)
            if not subj_ok and comp_in_tweet:
                drift_events.append(
                    {
                        "tweet_index": i,
                        "anchor_subject": subject,
                        "value": value,
                        "comparison_target": comparison,
                        "tweet_excerpt": tweet[:120],
                    }
                )
                reasons.append(
                    f"Relation drift tweet {i + 1}: '{value}' ({metric}) attributed near "
                    f"'{comparison}' but subject '{subject}' missing"
                )
                continue

            # Drift: value present, subject absent, no explicit comparison — unattributed metric
            if not subj_ok and value.lower() in lower:
                # Allow if tweet clearly discusses comparison_target as the slower/faster party
                # per relationship direction
                if relationship in ("higher_than", "slower_than", "worse_than"):
                    if comp_in_tweet and value in tweet:
                        drift_events.append(
                            {
                                "tweet_index": i,
                                "anchor_subject": subject,
                                "value": value,
                                "issue": "value_without_subject",
                                "tweet_excerpt": tweet[:120],
                            }
                        )
                        reasons.append(
                            f"Relation drift tweet {i + 1}: '{value}' used without anchor "
                            f"subject '{subject}'"
                        )

    # Dedupe reasons
    reasons = list(dict.fromkeys(reasons))
    passed = len(reasons) == 0
    return RelationalConsistencyResult(
        passed=passed,
        reasons=reasons,
        drift_events=drift_events,
    )


def evaluate_open_question_preservation(
    tweets: list[str],
    open_questions: list[dict],
) -> tuple[bool, list[str]]:
    """Ensure preserve_in_final questions are not aesthetically resolved away."""
    if not open_questions:
        return True, []

    thread = " ".join(tweets).lower()
    reasons: list[str] = []

    for oq in open_questions:
        if not oq.get("preserve_in_final", True):
            continue
        question = oq.get("question", "")
        q_tokens = set(re.findall(r"[a-zA-Z]{4,}", question.lower()))
        if not q_tokens:
            continue
        overlap = len(q_tokens & set(re.findall(r"[a-zA-Z]{4,}", thread)))
        ratio = overlap / len(q_tokens)

        # Must retain thematic presence OR explicit uncertainty
        uncertainty_markers = ["?", "unclear", "open question", "unresolved", "whether"]
        has_uncertainty = any(m in thread for m in uncertainty_markers)

        hypotheses = oq.get("competing_hypotheses") or []
        hyp_hit = any(
            h.lower()[:20] in thread for h in hypotheses if len(h) > 10
        )

        if ratio < 0.15 and not has_uncertainty and not hyp_hit:
            reasons.append(
                f"Open question not preserved in thread: '{question[:60]}...'"
            )

    return len(reasons) == 0, reasons
