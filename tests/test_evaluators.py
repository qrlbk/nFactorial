from app.utils.mechanistic_score import evaluate_mechanistic_density
from app.utils.semantic_density import evaluate_semantic_density
from app.utils.text_metrics import evaluate_thesis_alignment, evaluate_thread_length

SLOP_TEXT = """
In today's world, innovation is transforming the landscape of disruption.
Perhaps the ecosystem might evolve somewhat. It's important to note that
the paradigm shift bears mentioning as we move forward holistically.
"""

MECHANISTIC_TEXT = """
GPU scarcity drives inference costs up because supply constraints force
pricing power to chip vendors. The incentive to vertically integrate exists
since switching costs lock customers. Marginal adoption slows when unit
economics break at the constraint boundary.
"""

GOOD_TWEETS = [
    "GPU scarcity forces inference pricing up — chip vendors capture surplus.",
    "Vertical integration incentive exists because switching costs lock buyers.",
    "Supply constraints drive adoption slowdown at marginal unit economics break.",
    "Pricing power concentrates upstream when coordination fails at the bottleneck.",
    "Inference cost inflation compels buyers to absorb margin compression.",
    "The tradeoff: scale inference or accept constraint-driven margin erosion.",
]


def test_semantic_density_fails_on_slop():
    result = evaluate_semantic_density(SLOP_TEXT)
    assert not result.passed
    assert result.fluff_count > 0 or result.hedge_count > 2


def test_semantic_density_passes_mechanistic():
    result = evaluate_semantic_density(MECHANISTIC_TEXT)
    assert result.passed


def test_mechanistic_density_requires_layers():
    result = evaluate_mechanistic_density(MECHANISTIC_TEXT)
    assert result.passed
    assert result.mechanism_layers >= 2


def test_mechanistic_density_per_tweet_without_periods():
    """Each tweet is scored separately — threads rarely end tweets with periods."""
    tweets = "\n".join(
        [
            "NVIDIA CUDA lock-in forces inference pricing power because supply is constrained",
            "Every 10x GPU efficiency matched 10x parameter count — Jevons paradox for compute",
            "Distillation research won't collapse marginal inference cost if demand expands",
        ]
    )
    result = evaluate_mechanistic_density(tweets)
    assert result.mechanism_layers >= 2


def test_mechanistic_density_rag_style_operational():
    text = (
        "chunk 500 docs and rerank top 50 — latency spikes on every query. "
        "cost went UP because embedding calls + reranker + main LLM every query."
    )
    result = evaluate_mechanistic_density(text)
    assert result.mechanism_layers >= 2


def test_mechanistic_density_fails_thin_text():
    result = evaluate_mechanistic_density("AI is changing everything quickly.")
    assert not result.passed


def test_thread_length_valid():
    result = evaluate_thread_length(GOOD_TWEETS)
    assert result.passed
    assert result.tweet_count == 6


def test_thread_length_too_few():
    result = evaluate_thread_length(GOOD_TWEETS[:3])
    assert not result.passed


def test_thesis_alignment_pass():
    defended = "GPU scarcity forces inference pricing power to chip vendors"
    attacked = "AI scaling is unlimited and costs will always fall"
    result = evaluate_thesis_alignment(GOOD_TWEETS, defended, attacked)
    assert result.passed


def test_thesis_alignment_fail_consensus_drift():
    defended = "quantum entanglement enables faster-than-light travel"
    attacked = "physics limits are absolute"
    drift_tweets = [
        "Physics limits are absolute and cannot be violated ever.",
        "Scientists agree that relativity constrains all motion.",
        "The consensus view on speed limits is well established.",
        "No credible physicist disputes the speed of light cap.",
        "Experimental evidence consistently supports relativity.",
        "Therefore we must accept standard physical constraints.",
    ]
    result = evaluate_thesis_alignment(drift_tweets, defended, attacked)
    assert not result.passed
