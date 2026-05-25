from app.utils.input_worthiness import evaluate_input_worthiness

RU_CONTEXT = (
    "Мы снизили латентность RAG-пайплайна с 800 мс до 120 мс за три недели. "
    "Но retrieval всё ещё галлюцинирует на 12% запросов — реальная проблема в проде. "
    "Стоимость индексации выросла, маржа упала, вендор не заменяет наш деплой."
)

KK_CONTEXT = (
    "Біз RAG pipeline латенттігін 800 мс-тен 120 мс-ке дейін үш аптада төмендеттік. "
    "Бірақ retrieval 12% сұраныста қате жауап береді — нақты production мәселесі. "
    "Құны өсті, margin төмендеді, deploy өзімізде."
)


def test_russian_context_passes_gate():
    result = evaluate_input_worthiness(RU_CONTEXT, output_language="ru")
    assert result.metrics["word_count"] >= 25
    assert result.passed is True
    assert result.metrics["language"] == "ru"


def test_kazakh_context_passes_gate():
    result = evaluate_input_worthiness(KK_CONTEXT, output_language="kk")
    assert result.metrics["word_count"] >= 25
    assert result.passed is True


def test_cyrillic_context_detected_when_output_en():
    """UI locale/output mismatch: Cyrillic paste still counts words."""
    result = evaluate_input_worthiness(RU_CONTEXT, output_language="en")
    assert result.metrics["word_count"] >= 25
    assert result.metrics["language"] == "ru"
    assert result.passed is True


def test_english_only_word_count():
    text = (
        "We cut latency from 800ms to 120ms in three weeks but retrieval still fails "
        "12% of production queries. Real cost pressure on margin — vendor pricing "
        "does not replace our deploy pipeline or index benchmarks."
    )
    result = evaluate_input_worthiness(text, output_language="en")
    assert result.metrics["word_count"] >= 25
    assert result.passed is True
