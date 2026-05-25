from pydantic import BaseModel, Field


class ThesisPosition(BaseModel):
    attacked_consensus: str = Field(min_length=10)
    defended_claim: str = Field(min_length=10)
    strongest_counterargument: str = Field(min_length=10)
    why_counterargument_fails: str = Field(min_length=10)
    intellectual_risk_level: int = Field(ge=8, le=10)
    thesis_confidence: float = Field(ge=0.0, le=1.0)
