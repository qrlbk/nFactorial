"""Integration test with mocked LLM — no API keys required."""

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.builder import run_pipeline
from app.schemas.context import CausalAnchor, DistilledContext, InsightAnchor
from app.schemas.criticism import CriticismReport
from app.schemas.narrative import NarrativeFrame
from app.schemas.platform import ClaimVerification
from app.graph.nodes.fact_checker import FactCheckLLMOutput
from app.schemas.rewrite import RewriteOutput
from app.schemas.thesis import ThesisPosition

SAMPLE = open("tests/fixtures/sample_context.txt", encoding="utf-8").read()

DISTILLED = DistilledContext(
    consensus_view="LLM inference costs will approach zero via Moore's Law and distillation",
    why_consensus_is_wrong="Jevons paradox eats efficiency gains; parameter counts scale with capability",
    core_tension="Efficiency gains vs capability expansion on constrained GPU supply",
    asymmetric_insight="Inference pricing is a CUDA lock-in coordination game, not a transistor curve",
    second_order_effects=[
        "Moat shifts to eval infrastructure when tokens commoditize",
        "Wrapper startups face dual margin compression",
    ],
    falsifiable_claims=[
        "100x token cost drop in 24 months without demand expansion falsifies constraint thesis",
    ],
    causal_anchors=[
        CausalAnchor(
            subject="GPU supply chain",
            metric="latency",
            value="500-doc",
            relationship="higher_than",
            comparison_target="baseline retrieval",
            implication="infra pain dominates at scale",
        ),
    ],
    insight_anchors=[
        InsightAnchor(
            exact_observation="500-doc latency spikes killed usability",
            why_it_matters="Infra pain dominates retrieval quality in production",
            must_preserve=True,
        ),
        InsightAnchor(
            exact_observation="CUDA lock-in creates 18-month switching costs",
            why_it_matters="Pricing power stays with chip vendors not buyers",
            must_preserve=True,
        ),
    ],
)

THESIS = ThesisPosition(
    attacked_consensus="Inference will commoditize like compute historically did",
    defended_claim="GPU scarcity and switching costs keep inference pricing power with chip vendors",
    strongest_counterargument="Distillation and open models already collapsed margins 10x",
    why_counterargument_fails="Each 10x efficiency unlock matched 10x parameter scaling — net unit cost flat",
    intellectual_risk_level=9,
    thesis_confidence=0.88,
)

CRITIC_REJECT = CriticismReport(
    decision="REJECTED",
    cliche_detected=True,
    reasoning_flaw="Consensus restatement without violated assumption",
    slop_phrases_found=["paradigm shift", "game-changer"],
    verdict="REJECTED: sharpens consensus, no mechanism",
)

CRITIC_APPROVE = CriticismReport(
    decision="APPROVED",
    cliche_detected=False,
    reasoning_flaw="No material reasoning flaws detected",
    slop_phrases_found=[],
    verdict="APPROVED: mechanistic tension sustained",
)

NARRATIVE = NarrativeFrame(
    opening_conflict="Everyone prices inference like Moore's Law — suppliers price like oligopoly",
    violated_assumption="Efficiency automatically passes to buyers as lower prices",
    escalation_points=[
        "CUDA lock-in raises switching costs",
        "Jevons paradox on parameter scaling",
        "Hyperscaler subsidy masks negative unit economics",
    ],
    payoff="The moat is coordination and eval infra, not the model weights",
    final_reframe="You're not buying tokens — you're renting bottleneck access",
)

GOOD_TWEETS = RewriteOutput(
    tweets=[
        "500-doc latency spikes killed usability — GPU scarcity forces vendors to capture surplus via CUDA lock-in.",
        "Every 10x efficiency gain matched 10x parameter scaling. Jevons paradox ate the savings.",
        "Hyperscalers subsidize API pricing to own developer mindshare while unit economics stay negative.",
        "When tokens get cheap, moats shift to eval infrastructure — not model weights.",
        "Wrapper startups face margin compression from both hyperscaler subsidies and chip pricing power.",
        "Falsifiable: 100x token cost drop in 24mo without demand expansion kills this thesis.",
    ]
)


@pytest.mark.asyncio
async def test_pipeline_fail_closed_after_retries():
    """LLM critic may reject attempt 1; evaluator-certified drafts publish on retry 2+."""
    call_count = {"critic": 0}

    async def mock_invoke(*, node_name, prompt_name, input_vars, output_schema):
        if prompt_name == "research":
            return DISTILLED
        if prompt_name == "thesis":
            return THESIS
        if prompt_name == "critic":
            call_count["critic"] += 1
            return CRITIC_REJECT
        if prompt_name == "narrative":
            return NARRATIVE
        if prompt_name == "rewrite":
            return GOOD_TWEETS
        if prompt_name == "fact_checker":
            return FactCheckLLMOutput(claims=[ClaimVerification(claim="test", status="supported")])
        if prompt_name == "hooks":
            from app.graph.nodes.hooks import HookOutput
            return HookOutput(hooks=["hook1", "hook2", "hook3"])
        raise ValueError(f"unknown prompt {prompt_name}")

    with patch("app.graph.nodes.research.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.thesis.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.critic.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.narrative.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.rewrite.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.fact_checker.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.hooks.invoke_structured", AsyncMock(side_effect=mock_invoke)):
        result = await run_pipeline(raw_context=SAMPLE, mode="Contrarian VC")

    assert result.get("final_elite_thread")
    assert len(result.get("final_elite_thread", [])) >= 6
    assert call_count["critic"] >= 1


@pytest.mark.asyncio
async def test_pipeline_success_path():
    """Simulate approve on second critic pass after rewrite."""

    async def mock_invoke(*, node_name, prompt_name, input_vars, output_schema):
        if prompt_name == "research":
            return DISTILLED
        if prompt_name == "thesis":
            return THESIS
        if prompt_name == "critic":
            draft = input_vars.get("current_draft", "")
            if "1/" in draft or "GPU scarcity" in draft:
                return CRITIC_APPROVE
            return CRITIC_REJECT
        if prompt_name == "narrative":
            return NARRATIVE
        if prompt_name == "rewrite":
            return GOOD_TWEETS
        if prompt_name == "fact_checker":
            return FactCheckLLMOutput(claims=[ClaimVerification(claim="test", status="supported")])
        if prompt_name == "hooks":
            from app.graph.nodes.hooks import HookOutput
            return HookOutput(hooks=["hook1", "hook2", "hook3"])
        raise ValueError(f"unknown prompt {prompt_name}")

    with patch("app.graph.nodes.research.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.thesis.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.critic.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.narrative.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.rewrite.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.fact_checker.invoke_structured", AsyncMock(side_effect=mock_invoke)), \
         patch("app.graph.nodes.hooks.invoke_structured", AsyncMock(side_effect=mock_invoke)):
        result = await run_pipeline(raw_context=SAMPLE, mode="Contrarian VC")

    assert result.get("final_elite_thread")
    assert 6 <= len(result["final_elite_thread"]) <= 9
    assert result.get("eval_passed") is True
