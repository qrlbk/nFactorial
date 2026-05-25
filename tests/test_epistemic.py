from pathlib import Path

from app.utils.input_worthiness import evaluate_input_worthiness
from app.utils.specificity_score import evaluate_specificity

FIXTURES = Path(__file__).parent / "fixtures"


def test_weak_human_paste_refused():
    text = (FIXTURES / "human_paste_weak.txt").read_text(encoding="utf-8")
    result = evaluate_input_worthiness(text)
    assert not result.passed
    assert result.score < 0.45


def test_rag_human_paste_qualified():
    text = (FIXTURES / "human_paste_rag.txt").read_text(encoding="utf-8")
    result = evaluate_input_worthiness(text)
    assert result.passed
    assert result.metrics["operational_markers"] >= 2


def test_specificity_rejects_generic():
    result = evaluate_specificity("AI changes business incentives and transforms the landscape.")
    assert not result.passed


def test_specificity_passes_concrete():
    result = evaluate_specificity(
        "200k-token context windows increased retrieval cost faster than they reduced "
        "hallucination rates on compliance Q&A."
    )
    assert result.passed
