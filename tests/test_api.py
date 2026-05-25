"""API endpoint tests for enriched trace and templates."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.local_trace import TEMPLATE_DIR, TRACE_DIR, create_template
from app.services.trace_enrichment import compute_thread_stats, extract_key_insights

client = TestClient(app)


@pytest.fixture
def sample_trace_file(tmp_path, monkeypatch):
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    monkeypatch.setattr("app.services.local_trace.TRACE_DIR", trace_dir)
    monkeypatch.setattr("app.services.local_trace.TEMPLATE_DIR", template_dir)

    trace_id = "test-trace-001"
    payload = {
        "trace_id": trace_id,
        "created_at": "2026-05-24T12:00:00+00:00",
        "input": {"context_preview": "RAG is not solved latency 8s", "mode": "Contrarian VC"},
        "output": {"thread": ["Tweet one about RAG latency", "Tweet two about eval moat"]},
        "metadata": {
            "rejection_history": [],
            "total_retries": 1,
            "input_worthiness_score": 0.9,
            "pipeline_timeline": [
                {"node": "research_distiller", "status": "done", "duration_ms": 1200, "detail": "2 anchors"}
            ],
            "cognition_stages": {
                "consensus_analysis": {
                    "core_tension": "RAG infra vs model quality",
                    "causal_anchors": [
                        {
                            "subject": "RAG pipeline",
                            "metric": "latency",
                            "value": "8s",
                            "relationship": "higher_than",
                            "comparison_target": "baseline",
                            "implication": "users churn",
                        }
                    ],
                    "open_questions": [
                        {
                            "question": "Is eval harness the real moat?",
                            "why_unresolved": "No public benchmarks",
                            "competing_hypotheses": [],
                            "preserve_in_final": True,
                        }
                    ],
                    "consensus_view": "x",
                    "why_consensus_is_wrong": "y",
                    "asymmetric_insight": "z",
                    "second_order_effects": ["a"],
                    "falsifiable_claims": ["b"],
                }
            },
        },
    }
    (trace_dir / f"{trace_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    return trace_id


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_public_config():
    resp = client.get("/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service_name"] == "Adversarial Editorial Engine"
    assert len(data["editor_modes"]) >= 3
    assert "min_thesis_confidence" in data["thresholds"]


def test_list_traces_empty():
    resp = client.get("/traces")
    assert resp.status_code == 200
    assert "traces" in resp.json()


def test_get_trace_enriched(sample_trace_file):
    resp = client.get(f"/trace/{sample_trace_file}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["output_thread"]
    assert data["pipeline_timeline"]
    assert data["key_insights"]


def test_templates_crud(sample_trace_file):
    create_resp = client.post(
        "/templates",
        json={
            "name": "RAG pain",
            "description": "Ops notes",
            "context": "RAG latency is painful in production with 500 docs and re-indexing weekly",
            "default_mode": "Contrarian VC",
        },
    )
    assert create_resp.status_code == 200
    template_id = create_resp.json()["id"]

    list_resp = client.get("/templates")
    assert list_resp.status_code == 200
    assert any(t["id"] == template_id for t in list_resp.json()["templates"])

    delete_resp = client.delete(f"/templates/{template_id}")
    assert delete_resp.status_code == 200


def test_thread_stats_helpers():
    tweets = ["Because GPU supply constrains latency, RAG pipelines face incentive misalignment."]
    stats = compute_thread_stats(tweets)
    assert stats is not None
    assert stats.tweet_count == 1

    insights = extract_key_insights(
        {
            "core_tension": "Infra pain dominates",
            "causal_anchors": [],
            "falsifiable_claims": [],
            "open_questions": [],
            "asymmetric_insight": "Moat is eval",
        }
    )
    assert insights
