"""Tests for i18n module and localized API responses."""

import pytest
from fastapi.testclient import TestClient

from app.i18n import localized_refusal, normalize_locale, t
from app.main import app
from app.services.trace_enrichment import build_public_config, compute_thread_stats

client = TestClient(app)


def test_normalize_locale():
    assert normalize_locale("ru-RU") == "ru"
    assert normalize_locale("kk") == "kk"
    assert normalize_locale("fr") == "en"


def test_refusal_russian():
    text = localized_refusal("ru", "EPISTEMIC")
    assert "отклонена" in text.lower() or "Generation" not in text


def test_refusal_kazakh():
    text = localized_refusal("kk", "THESIS")
    assert len(text) > 20


def test_config_locale_kk():
    resp = client.get("/config?locale=kk")
    assert resp.status_code == 200
    modes = resp.json()["editor_modes"]
    assert any("Contrarian" in m["label"] for m in modes)
    assert any("асимметрия" in m["description"].lower() or "кonsensus" in m["description"].lower() for m in modes)


def test_signal_density_label_localized():
    stats = compute_thread_stats(
        ["Because GPU supply constrains latency, RAG pipelines face incentive misalignment."],
        locale="ru",
    )
    assert stats is not None
    assert stats.signal_density_label in ("Высокая", "Средняя", "Низкая")


def test_pipeline_detail_translation():
    detail = t("ru", "pipeline.detail.research", anchors=3, questions=1)
    assert "3" in detail


def test_evaluator_reason_kazakh():
    from app.i18n.evaluator_reasons import translate_evaluator_reason

    reason = (
        "Mechanism layers 0 below minimum 2; "
        "Defended claim overlap 0.00 below 0.15; "
        "Specificity score 0.22 below 0.35 (need numbers, named systems, or operational nouns)"
    )
    translated = translate_evaluator_reason(reason, "kk")
    assert "Механизм" in translated
    assert "тезис" in translated.lower() or "сәйкестік" in translated
    assert "Mechanism layers" not in translated


def test_refusal_quality_exhausted_message():
    from app.graph.nodes.refuse import _build_retry_exhausted_reason

    reason = _build_retry_exhausted_reason(
        {
            "response_locale": "kk",
            "total_retry_count": 3,
            "rejection_history": [
                {
                    "node": "deterministic_evaluators",
                    "reason": "Relation drift tweet 1: 'went UP' (cost) attributed near 'initial expectations'",
                }
            ],
        }
    )
    assert "Жоба" in reason or "сapа" in reason.lower()
    assert "Relation drift" in reason
    assert "3" in reason
