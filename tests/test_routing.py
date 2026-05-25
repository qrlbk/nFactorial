from app.graph.routing import (
    route_after_context_gate,
    route_after_critic,
    route_after_evaluators,
    route_after_rewrite,
    route_after_thesis,
)


def test_context_gate_refuse():
    assert route_after_context_gate({"context_qualified": False}) == "refuse"


def test_context_gate_qualified():
    assert route_after_context_gate({"context_qualified": True}) == "research"


def test_context_gate_retrieval():
    assert route_after_context_gate({"context_qualified": True, "source_urls": ["https://example.com"]}) == "retrieval"


def test_thesis_refuse_on_low_confidence():
    assert route_after_thesis({"refusal_reason": "low confidence"}) == "refuse"


def test_route_after_evaluators_to_critic():
    state = {"total_retry_count": 0, "eval_passed": True}
    assert route_after_evaluators(state) == "critic"


def test_route_after_evaluators_to_writer():
    state = {"total_retry_count": 0, "eval_passed": False}
    assert route_after_evaluators(state) == "writer"


def test_route_after_critic_to_post():
    state = {"total_retry_count": 0, "last_critic_report": {"decision": "APPROVED"}}
    assert route_after_critic(state) == "post"


def test_route_after_critic_skip_post():
    state = {"total_retry_count": 0, "last_critic_report": {"decision": "APPROVED"}, "skip_post_pipeline": True}
    assert route_after_critic(state) == "end"


def test_route_after_rewrite_to_evaluators():
    assert route_after_rewrite({}) == "evaluators"
