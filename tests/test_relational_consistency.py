from app.utils.relational_consistency import evaluate_relational_consistency


def test_fintech_latency_relation_drift_detected():
    """The classic bug: 8s belongs to GPT-4o full-context, not RAG."""
    anchors = [
        {
            "subject": "GPT-4o full-context",
            "metric": "latency",
            "value": "8s",
            "relationship": "higher_than",
            "comparison_target": "RAG pipeline (1.2s)",
            "implication": "full-context retrieval scales poorly",
        }
    ]
    bad_tweets = [
        "With RAG, latency of 8s vs 1.2s leads to user churn.",
        "Fine-tuning wins on precision in stable regulatory contexts.",
        "Retrain cost ~$400 plus 2 eng-weeks vs re-index $80/week.",
        "RAG on 1200 pdf precision 62% vs fine-tune 89%.",
        "Compliance bots need precision not just recall.",
        "Eval harness may be the real moat not the model.",
    ]
    result = evaluate_relational_consistency(bad_tweets, anchors)
    assert not result.passed
    assert any("drift" in r.lower() for r in result.reasons)


def test_operational_costs_singular_matches_plural_anchor():
    """cost in tweet should satisfy Operational costs anchor subject."""
    anchors = [
        {
            "subject": "Operational costs",
            "metric": "direction",
            "value": "went UP",
            "relationship": "higher_than",
            "comparison_target": "initial expectations",
            "implication": "RAG ops cost surprise",
        }
    ]
    tweets = [
        "cost actually went UP not down bc we pay for embedding calls + reranker + main LLM every query.",
        "Retrieval quality plateaus after ~2 weeks when docs change.",
        "Continuous re-indexing pipelines, eval sets, human labelers — that's where the money goes.",
        "200k context != finding the right paragraph; attention dilution on compliance Q&A.",
        "RAG vendors selling drop-in vector search lose to vertical eval infra.",
        "Open question: fine-tuning small models vs RAG for stable corp knowledge.",
    ]
    result = evaluate_relational_consistency(tweets, anchors)
    assert result.passed

    anchors = [
        {
            "subject": "GPT-4o full-context",
            "metric": "latency",
            "value": "8s",
            "relationship": "higher_than",
            "comparison_target": "RAG pipeline (1.2s)",
            "implication": "full-context retrieval scales poorly",
        }
    ]
    good_tweets = [
        "GPT-4o full-context hit 8s latency vs 1.2s on our RAG path — users churned.",
        "Fine-tune gpt-4o-mini on 800 Q&A pairs -> 89% vs RAG precision 62%.",
        "Retrain ~$400 + 2 eng-weeks vs re-index $80/week when regs change.",
        "Stable regs: fine-tune wins. Volatile docs: RAG wins. Hybrid = ops hell.",
        "Is the real moat the eval harness not the model? Still open.",
        "Compliance precision beats adaptability when stakes are regulatory.",
    ]
    result = evaluate_relational_consistency(good_tweets, anchors)
    assert result.passed
