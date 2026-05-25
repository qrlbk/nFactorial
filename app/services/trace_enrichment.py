from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.i18n import normalize_locale, t, translate_refusal_if_known
from app.i18n.evaluator_reasons import localize_pipeline_timeline, localize_rejection_history
from app.schemas.api import (
    EditorModePreset,
    GenerateResponse,
    PipelineStepRecord,
    PublicConfigResponse,
    ThreadStats,
    TraceResponse,
)
from app.utils.mechanistic_score import evaluate_mechanistic_density
from app.utils.semantic_density import evaluate_semantic_density
from app.utils.specificity_score import evaluate_specificity

MODE_IDS = ["contrarian-vc", "paul-graham", "research-analyst"]


def _signal_density_label(score: float, locale: str) -> str:
    if score >= 0.7:
        return t(locale, "stats.density.high")
    if score >= 0.45:
        return t(locale, "stats.density.medium")
    return t(locale, "stats.density.low")


def _question_preserved(question: str, tweets: list[str]) -> bool:
    if not question or not tweets:
        return False
    blob = " ".join(tweets).lower()
    tokens = [tok for tok in question.lower().split() if len(tok) > 4][:6]
    if not tokens:
        return False
    hits = sum(1 for tok in tokens if tok in blob)
    return hits >= max(1, len(tokens) // 2)


def extract_key_insights(
    distilled_context: dict[str, Any] | None,
    *,
    max_items: int = 12,
) -> list[str]:
    if not distilled_context:
        return []

    insights: list[str] = []
    tension = distilled_context.get("core_tension")
    if tension:
        insights.append(str(tension)[:100])

    for anchor in distilled_context.get("causal_anchors") or []:
        subject = anchor.get("subject", "")
        metric = anchor.get("metric", "")
        value = anchor.get("value", "")
        if subject and value:
            insights.append(f"{subject}: {metric} {value}".strip()[:100])

    for claim in distilled_context.get("falsifiable_claims") or []:
        insights.append(str(claim)[:100])

    for question in distilled_context.get("open_questions") or []:
        q = question.get("question") if isinstance(question, dict) else str(question)
        if q:
            insights.append(str(q)[:100])

    asymmetric = distilled_context.get("asymmetric_insight")
    if asymmetric:
        insights.append(str(asymmetric)[:100])

    deduped: list[str] = []
    seen: set[str] = set()
    for item in insights:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_items:
            break
    return deduped


def compute_thread_stats(
    tweets: list[str] | None,
    *,
    distilled_context: dict[str, Any] | None = None,
    borderline_input: bool = False,
    eval_passed: bool = False,
    locale: str = "en",
) -> ThreadStats | None:
    if not tweets:
        return None

    loc = normalize_locale(locale)
    text = "\n".join(tweets)
    semantic = evaluate_semantic_density(text)
    mechanistic = evaluate_mechanistic_density(text)
    specificity = evaluate_specificity(text)

    signal_density = max(0.0, min(1.0, 1.0 - semantic.abstract_noun_density * 4 + specificity.score * 0.4))

    open_questions = []
    if distilled_context:
        open_questions = [
            q.get("question", "")
            for q in distilled_context.get("open_questions") or []
            if isinstance(q, dict)
        ]

    open_preserved = any(_question_preserved(q, tweets) for q in open_questions) if open_questions else True
    uncertainty_kept = borderline_input or semantic.hedge_count > 0
    no_false_closure = open_preserved if open_questions else True

    return ThreadStats(
        tweet_count=len(tweets),
        total_characters=sum(len(tw) for tw in tweets),
        signal_density=round(signal_density, 2),
        signal_density_label=_signal_density_label(signal_density, loc),
        mechanistic_layers=mechanistic.mechanism_layers,
        mechanistic_layers_target=2,
        epistemic_preserved=eval_passed and no_false_closure,
        open_question_preserved=open_preserved,
        uncertainty_signals_kept=uncertainty_kept,
        no_false_closure=no_false_closure,
    )


def build_public_config(*, locale: str = "en") -> PublicConfigResponse:
    settings = get_settings()
    loc = normalize_locale(locale)
    tracing_source = "langfuse" if settings.langfuse_public_key and settings.langfuse_secret_key else "local"
    editor_modes = [
        EditorModePreset(
            id=mode_id,
            label=t(loc, f"modes.{mode_id}.label"),
            description=t(loc, f"modes.{mode_id}.description"),
        )
        for mode_id in MODE_IDS
    ]
    return PublicConfigResponse(
        service_name="Adversarial Editorial Engine",
        tracing_source=tracing_source,
        editor_modes=editor_modes,
        thresholds={
            "min_thesis_confidence": settings.min_thesis_confidence,
            "min_input_worthiness_score": settings.min_input_worthiness_score,
            "min_specificity_score": settings.min_specificity_score,
            "min_anchor_preservation_ratio": settings.min_anchor_preservation_ratio,
            "max_critic_retries": settings.max_critic_retries,
            "thread_min": settings.thread_min,
            "thread_max": settings.thread_max,
            "tweet_max_chars": settings.tweet_max_chars,
        },
    )


def enrich_pipeline_result(result: dict[str, Any], *, locale: str = "en") -> dict[str, Any]:
    tweets = result.get("final_elite_thread") or []
    distilled = result.get("distilled_context") or {}
    timeline = result.get("pipeline_timeline") or []
    loc = normalize_locale(locale)
    stats = compute_thread_stats(
        tweets,
        distilled_context=distilled,
        borderline_input=bool(result.get("borderline_input")),
        eval_passed=bool(result.get("eval_passed")),
        locale=loc,
    )
    refusal = translate_refusal_if_known(loc, result.get("refusal_reason")) or result.get(
        "refusal_reason"
    )
    timeline = localize_pipeline_timeline(list(timeline), loc)
    rejection_history = localize_rejection_history(
        list(result.get("rejection_history") or []),
        loc,
    )
    return {
        **result,
        "refusal_reason": refusal,
        "rejection_history": rejection_history,
        "thread_stats": stats.model_dump() if stats else None,
        "key_insights": extract_key_insights(distilled),
        "pipeline_timeline": timeline,
    }


def build_generate_response(result: dict[str, Any], *, locale: str = "en") -> GenerateResponse:
    loc = normalize_locale(locale or result.get("response_locale", "en"))
    enriched = enrich_pipeline_result(result, locale=loc)
    refused = bool(enriched.get("refusal_reason")) or (
        not enriched.get("final_elite_thread")
        and not (enriched.get("thesis_candidates") or enriched.get("final_output", {}).get("thesis_candidates"))
    )
    stats = enriched.get("thread_stats")
    timeline = enriched.get("pipeline_timeline") or []

    return GenerateResponse(
        final_thread=enriched.get("final_elite_thread") or None,
        trace_id=enriched.get("trace_id"),
        rejection_history=enriched.get("rejection_history", []),
        refused=refused,
        refusal_reason=enriched.get("refusal_reason"),
        pipeline_log=enriched.get("pipeline_log", []),
        pipeline_timeline=[PipelineStepRecord(**item) for item in timeline],
        thread_stats=ThreadStats(**stats) if stats else None,
        key_insights=enriched.get("key_insights", []),
        total_retries=enriched.get("total_retry_count", 0),
        input_worthiness_score=float(enriched.get("input_worthiness_score") or 0.0),
        output_type=enriched.get("output_type", "thread"),
        thesis_candidates=enriched.get("thesis_candidates") or enriched.get("final_output", {}).get("thesis_candidates", []),
        final_output=enriched.get("final_output", {}),
        hook_variants=enriched.get("hook_variants") or enriched.get("final_output", {}).get("hook_variants", []),
        fact_check_report=enriched.get("fact_check_report") or enriched.get("final_output", {}).get("fact_check_report", {}),
    )


def build_trace_response(
    trace_id: str,
    summary: dict[str, Any],
    *,
    langfuse_url: str | None = None,
    locale: str = "en",
) -> TraceResponse:
    loc = normalize_locale(locale)
    metadata = summary.get("metadata") or {}
    inp = summary.get("input") or {}
    output = summary.get("output") or {}

    rejection_chain = metadata.get("rejection_history") or []
    if not rejection_chain and summary.get("events"):
        rejection_chain = [
            e.get("metadata", {})
            for e in summary["events"]
            if e.get("name") == "rejection"
        ]

    cognition = metadata.get("cognition_stages") or {}
    pipeline_log = cognition.get("editorial_revision") or []
    if isinstance(pipeline_log, str):
        pipeline_log = [pipeline_log]

    pipeline_timeline = metadata.get("pipeline_timeline") or []
    distilled = cognition.get("consensus_analysis") or {}

    output_thread = output.get("thread") if isinstance(output, dict) else None
    refusal_reason = translate_refusal_if_known(
        loc,
        output.get("refusal") if isinstance(output, dict) else None,
    )
    status = "success" if output_thread else "refused"

    stats = compute_thread_stats(
        output_thread,
        distilled_context=distilled,
        borderline_input=bool(metadata.get("borderline_input")),
        eval_passed=status == "success",
        locale=loc,
    )

    return TraceResponse(
        trace_id=trace_id,
        rejection_chain=rejection_chain,
        cognition_stages=cognition,
        langfuse_url=langfuse_url,
        output_thread=output_thread,
        refusal_reason=refusal_reason,
        input_preview=inp.get("context_preview", ""),
        mode=inp.get("mode", ""),
        total_retries=int(metadata.get("total_retries") or 0),
        input_worthiness_score=float(metadata.get("input_worthiness_score") or 0.0),
        pipeline_log=pipeline_log,
        pipeline_timeline=[PipelineStepRecord(**item) for item in pipeline_timeline],
        thread_stats=stats,
        key_insights=extract_key_insights(distilled),
        status=status,
    )
