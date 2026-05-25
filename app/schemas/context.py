from pydantic import BaseModel, Field, field_validator


class CausalAnchor(BaseModel):
    subject: str = Field(min_length=2)
    metric: str = Field(min_length=2)
    value: str = Field(min_length=1)
    relationship: str = Field(min_length=2)
    comparison_target: str = Field(default="")
    implication: str = Field(min_length=5)


class InsightAnchor(BaseModel):
    """Legacy flat anchor — kept for backward compatibility in tests."""
    exact_observation: str = Field(min_length=5)
    why_it_matters: str = Field(min_length=5)
    must_preserve: bool = True


class OpenQuestion(BaseModel):
    question: str = Field(min_length=5)
    why_unresolved: str = Field(min_length=5)
    competing_hypotheses: list[str] = Field(default_factory=list)
    preserve_in_final: bool = True


class DistilledContext(BaseModel):
    consensus_view: str = Field(min_length=10)
    why_consensus_is_wrong: str = Field(min_length=10)
    core_tension: str = Field(min_length=10)
    asymmetric_insight: str = Field(min_length=10)
    second_order_effects: list[str] = Field(min_length=1)
    falsifiable_claims: list[str] = Field(min_length=1)
    causal_anchors: list[CausalAnchor] = Field(min_length=1)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    insight_anchors: list[InsightAnchor] = Field(default_factory=list)

    @field_validator("second_order_effects", "falsifiable_claims")
    @classmethod
    def non_empty_items(cls, v: list[str]) -> list[str]:
        if not all(item.strip() for item in v):
            raise ValueError("All list items must be non-empty")
        return v
