from __future__ import annotations

import time
from typing import Any, Callable, Awaitable

from app.graph.pipeline_timeline import (
    append_thread_assembler,
    append_timeline_entry,
    infer_detail,
    infer_status,
)
from app.graph.nodes.context_gate import context_qualification_gate_node
from app.graph.nodes.critic import anti_slop_critic_node
from app.graph.nodes.distribution import distribution_node
from app.graph.nodes.evaluators import deterministic_evaluators_node
from app.graph.nodes.fact_checker import fact_checker_node
from app.graph.nodes.hooks import hook_generator_node
from app.graph.nodes.narrative import narrative_architect_node
from app.graph.nodes.refuse import refuse_node
from app.graph.nodes.research import research_distiller_node
from app.graph.nodes.thesis import thesis_commitment_node
from app.graph.nodes.thesis_angles import thesis_angles_node
from app.graph.nodes.writer_dispatch import writer_dispatch_node
from app.services.content_fetcher import retrieval_node
from app.graph.routing import (
    route_after_context_gate,
    route_after_critic,
    route_after_evaluators,
    route_after_fact_check,
    route_after_thesis,
    route_after_thesis_angles,
)
from app.graph.state import EditorialState, OutputType
from app.services.tracing import editorial_trace, finalize_trace
from app.services.voice_profiler import get_voice

from langgraph.graph import END, StateGraph

NODE_TRACE_NAMES: dict[str, str] = {
    "research": "research_distiller",
    "retrieval": "retrieval_agent",
    "context_gate": "context_qualification_gate",
    "thesis_angles": "thesis_angles_generator",
    "thesis": "thesis_commitment",
    "critic": "anti_slop_critic",
    "narrative": "narrative_architect",
    "writer": "high_pressure_rewriter",
    "evaluators": "deterministic_evaluators",
    "fact_check": "fact_checker",
    "hooks": "hook_generator",
    "distribution": "distribution_agent",
    "refuse": "refuse",
}


def _wrap_with_trace(
    node_fn: Callable[..., Awaitable[dict[str, Any]]],
    graph_key: str,
) -> Callable[..., Awaitable[dict[str, Any]]]:
    trace_name = NODE_TRACE_NAMES.get(graph_key, graph_key)
    passes_trace = trace_name in (
        "context_qualification_gate",
        "anti_slop_critic",
        "deterministic_evaluators",
    )

    async def wrapped(state: dict[str, Any]) -> dict[str, Any]:
        trace = state.get("_trace")
        timeline = list(state.get("pipeline_timeline", []))
        started = time.perf_counter()

        if passes_trace:
            result = await node_fn(state, trace=trace)
        else:
            result = await node_fn(state)

        duration_ms = int((time.perf_counter() - started) * 1000)
        merged = {**state, **result}
        status = infer_status(trace_name, merged, state.get("pipeline_log", []))
        detail = infer_detail(trace_name, merged, state)
        timeline = append_timeline_entry(
            timeline=timeline,
            node=trace_name,
            status=status,
            duration_ms=duration_ms,
            detail=detail,
        )
        result["pipeline_timeline"] = timeline
        return result

    wrapped.__name__ = graph_key
    return wrapped


def _finalize_output(state: dict[str, Any]) -> dict[str, Any]:
    output_type = state.get("output_type", "thread")
    tweets = state.get("final_elite_thread") or state.get("current_tweets") or []
    final_output = dict(state.get("final_output") or {})
    final_output.update(
        {
            "output_type": output_type,
            "content": tweets if output_type != "essay" and output_type != "article" else state.get("current_draft", ""),
            "essay_sections": state.get("essay_sections", []),
            "hook_variants": state.get("hook_variants", []),
            "fact_check_report": state.get("fact_check_report", {}),
            "thesis_candidates": state.get("thesis_candidates", []),
        }
    )
    update: dict[str, Any] = {"final_output": final_output}
    if output_type in ("essay", "article"):
        update["final_elite_thread"] = []
    elif tweets:
        update["final_elite_thread"] = tweets
    return update


def build_graph(*, include_thesis_angles: bool = False):
    graph = StateGraph(EditorialState)

    graph.add_node("context_gate", _wrap_with_trace(context_qualification_gate_node, "context_gate"))
    graph.add_node("retrieval", _wrap_with_trace(retrieval_node, "retrieval"))
    graph.add_node("research", _wrap_with_trace(research_distiller_node, "research"))
    if include_thesis_angles:
        graph.add_node("thesis_angles", _wrap_with_trace(thesis_angles_node, "thesis_angles"))
    graph.add_node("thesis", _wrap_with_trace(thesis_commitment_node, "thesis"))
    graph.add_node("narrative", _wrap_with_trace(narrative_architect_node, "narrative"))
    graph.add_node("writer", _wrap_with_trace(writer_dispatch_node, "writer"))
    graph.add_node("evaluators", _wrap_with_trace(deterministic_evaluators_node, "evaluators"))
    graph.add_node("critic", _wrap_with_trace(anti_slop_critic_node, "critic"))
    graph.add_node("fact_check", _wrap_with_trace(fact_checker_node, "fact_check"))
    graph.add_node("hooks", _wrap_with_trace(hook_generator_node, "hooks"))
    graph.add_node("distribution", _wrap_with_trace(distribution_node, "distribution"))
    graph.add_node("refuse", _wrap_with_trace(refuse_node, "refuse"))

    graph.set_entry_point("context_gate")

    graph.add_conditional_edges(
        "context_gate",
        route_after_context_gate,
        {"retrieval": "retrieval", "research": "research", "refuse": "refuse"},
    )
    graph.add_edge("retrieval", "research")

    if include_thesis_angles:
        graph.add_edge("research", "thesis_angles")
        graph.add_conditional_edges(
            "thesis_angles",
            route_after_thesis_angles,
            {"thesis": "thesis", "narrative": "narrative", "writer": "writer", "end": END, "refuse": "refuse"},
        )
    else:
        graph.add_edge("research", "thesis")

    graph.add_conditional_edges(
        "thesis",
        route_after_thesis,
        {"narrative": "narrative", "writer": "writer", "refuse": "refuse"},
    )
    graph.add_edge("narrative", "writer")
    graph.add_edge("writer", "evaluators")

    graph.add_conditional_edges(
        "evaluators",
        route_after_evaluators,
        {"critic": "critic", "writer": "writer", "refuse": "refuse"},
    )

    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {"end": END, "writer": "writer", "refuse": "refuse", "post": "fact_check"},
    )

    graph.add_conditional_edges(
        "fact_check",
        route_after_fact_check,
        {"hooks": "hooks", "writer": "writer", "refuse": "refuse"},
    )
    graph.add_edge("hooks", "distribution")
    graph.add_edge("distribution", END)
    graph.add_edge("refuse", END)

    return graph.compile()


def _build_initial_state(
    *,
    raw_context: str,
    mode: str,
    output_language: str,
    response_locale: str,
    output_type: OutputType,
    source_urls: list[str] | None = None,
    selected_thesis_id: str | None = None,
    voice_profile_id: str | None = None,
    quoted_tweet: str = "",
    thesis_only: bool = False,
    skip_post_pipeline: bool = False,
    autonomous_research: bool = False,
    research_topic: str | None = None,
    generate_thesis_angles: bool = False,
) -> dict[str, Any]:
    voice_guidelines: dict[str, Any] = {}
    if voice_profile_id:
        profile = get_voice(voice_profile_id)
        if profile:
            voice_guidelines = profile.get("guidelines", {})

    return {
        "raw_context": raw_context,
        "selected_mode": mode,
        "output_type": output_type,
        "quoted_tweet": quoted_tweet,
        "output_language": output_language,
        "response_locale": response_locale,
        "source_urls": source_urls or [],
        "selected_thesis_id": selected_thesis_id,
        "voice_profile_id": voice_profile_id,
        "voice_guidelines": voice_guidelines,
        "thesis_only": thesis_only,
        "skip_post_pipeline": skip_post_pipeline,
        "autonomous_research": autonomous_research,
        "research_topic": research_topic,
        "distilled_context": {},
        "thesis_position": {},
        "thesis_candidates": [],
        "narrative_frame": {},
        "current_draft": "",
        "current_tweets": [],
        "essay_sections": [],
        "last_critic_report": {},
        "rejection_history": [],
        "critic_attempts": 0,
        "rewrite_attempts": 0,
        "total_retry_count": 0,
        "final_elite_thread": [],
        "final_output": {},
        "refusal_reason": None,
        "trace_id": None,
        "pipeline_log": [],
        "pipeline_timeline": [],
        "eval_passed": False,
        "narrative_completed": False,
        "context_qualified": False,
        "input_worthiness_score": 0.0,
        "borderline_input": False,
        "critic_strictness_boost": 0.0,
        "source_documents": [],
        "retrieved_chunks": [],
        "fact_check_report": {},
        "hook_variants": [],
        "_generate_thesis_angles": generate_thesis_angles,
    }


async def run_pipeline(
    *,
    raw_context: str,
    mode: str = "Contrarian VC",
    output_language: str = "en",
    response_locale: str = "en",
    output_type: OutputType = "thread",
    source_urls: list[str] | None = None,
    selected_thesis_id: str | None = None,
    voice_profile_id: str | None = None,
    quoted_tweet: str = "",
    thesis_only: bool = False,
    skip_post_pipeline: bool = False,
    autonomous_research: bool = False,
    research_topic: str | None = None,
    generate_thesis_angles: bool = False,
) -> dict[str, Any]:
    initial = _build_initial_state(
        raw_context=raw_context,
        mode=mode,
        output_language=output_language,
        response_locale=response_locale,
        output_type=output_type,
        source_urls=source_urls,
        selected_thesis_id=selected_thesis_id,
        voice_profile_id=voice_profile_id,
        quoted_tweet=quoted_tweet,
        thesis_only=thesis_only,
        skip_post_pipeline=skip_post_pipeline,
        autonomous_research=autonomous_research,
        research_topic=research_topic,
        generate_thesis_angles=generate_thesis_angles,
    )

    include_angles = generate_thesis_angles or thesis_only or bool(selected_thesis_id)

    with editorial_trace(context_preview=raw_context, mode=mode) as (trace, trace_id):
        initial["_trace"] = trace
        initial["trace_id"] = trace_id

        compiled = build_graph(include_thesis_angles=include_angles)
        result = await compiled.ainvoke(initial)

        timeline = list(result.get("pipeline_timeline") or [])
        tweets = result.get("final_elite_thread") or []
        if tweets:
            timeline = append_thread_assembler(
                timeline,
                len(tweets),
                locale=result.get("response_locale", "en"),
            )
        result["pipeline_timeline"] = timeline
        result.update(_finalize_output(result))

        if trace:
            output_payload: dict[str, Any] = {}
            if result.get("final_elite_thread"):
                output_payload["thread"] = result.get("final_elite_thread")
            elif result.get("current_draft") and output_type in ("essay", "article"):
                output_payload["essay"] = result.get("current_draft")
            elif result.get("thesis_candidates") and not result.get("final_elite_thread"):
                output_payload["thesis_candidates"] = result.get("thesis_candidates")
            elif result.get("refusal_reason"):
                output_payload["refusal"] = result.get("refusal_reason")

            finalize_trace(
                trace,
                output=output_payload or {"refusal": result.get("refusal_reason")},
                metadata={
                    "rejection_history": result.get("rejection_history", []),
                    "total_retries": result.get("total_retry_count", 0),
                    "input_worthiness_score": result.get("input_worthiness_score"),
                    "borderline_input": result.get("borderline_input", False),
                    "output_language": result.get("output_language", "en"),
                    "response_locale": result.get("response_locale", "en"),
                    "output_type": output_type,
                    "pipeline_timeline": timeline,
                    "final_output": result.get("final_output", {}),
                    "cognition_stages": {
                        "consensus_analysis": result.get("distilled_context"),
                        "thesis_commitment": result.get("thesis_position"),
                        "thesis_candidates": result.get("thesis_candidates"),
                        "adversarial_review": result.get("last_critic_report"),
                        "narrative_compression": result.get("narrative_frame"),
                        "fact_check": result.get("fact_check_report"),
                        "editorial_revision": result.get("pipeline_log"),
                    },
                },
            )

        result.pop("_trace", None)
        return result
