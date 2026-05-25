from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class CriticismReport(BaseModel):
    decision: Literal["APPROVED", "REJECTED"]
    cliche_detected: bool
    reasoning_flaw: str = Field(default="")
    slop_phrases_found: list[str]
    verdict: str = Field(min_length=5)

    @field_validator("reasoning_flaw", mode="before")
    @classmethod
    def coerce_reasoning_flaw(cls, v: object) -> str:
        if v is None:
            return ""
        return str(v)

    @model_validator(mode="after")
    def validate_reasoning_flaw(self) -> "CriticismReport":
        if self.decision == "REJECTED" and not self.reasoning_flaw.strip():
            raise ValueError("reasoning_flaw required when REJECTED")
        if self.decision == "APPROVED" and not self.reasoning_flaw.strip():
            self.reasoning_flaw = "No material reasoning flaws detected"
        return self

    @field_validator("verdict")
    @classmethod
    def no_soft_language(cls, v: str) -> str:
        soft = ["maybe", "perhaps", "somewhat", "could be", "might be", "it seems"]
        lower = v.lower()
        for phrase in soft:
            if phrase in lower:
                raise ValueError(f"Soft language forbidden in verdict: {phrase}")
        return v
