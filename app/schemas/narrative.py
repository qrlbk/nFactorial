from pydantic import BaseModel, Field, field_validator


class NarrativeFrame(BaseModel):
    opening_conflict: str = Field(min_length=10)
    violated_assumption: str = Field(min_length=10)
    escalation_points: list[str] = Field(min_length=2)
    payoff: str = Field(min_length=10)
    final_reframe: str = Field(min_length=10)

    @field_validator("escalation_points")
    @classmethod
    def non_empty_escalation(cls, v: list[str]) -> list[str]:
        if not all(item.strip() for item in v):
            raise ValueError("All escalation points must be non-empty")
        return v
