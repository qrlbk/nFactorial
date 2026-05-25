import pytest
from pydantic import ValidationError

from app.schemas.thesis import ThesisPosition


def test_thesis_risk_level_must_be_high():
    with pytest.raises(ValidationError):
        ThesisPosition(
            attacked_consensus="Everyone believes X is inevitable",
            defended_claim="X fails because incentive structures invert",
            strongest_counterargument="Historical precedent shows X succeeded",
            why_counterargument_fails="Precedent ignores second-order supply constraints",
            intellectual_risk_level=7,
            thesis_confidence=0.9,
        )


def test_thesis_risk_level_valid():
    thesis = ThesisPosition(
        attacked_consensus="Everyone believes X is inevitable",
        defended_claim="X fails because incentive structures invert",
        strongest_counterargument="Historical precedent shows X succeeded",
        why_counterargument_fails="Precedent ignores second-order supply constraints",
        intellectual_risk_level=9,
        thesis_confidence=0.85,
    )
    assert thesis.thesis_confidence == 0.85
