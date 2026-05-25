from datetime import datetime

from pydantic import BaseModel, Field


class RejectionEvent(BaseModel):
    node: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str = Field(min_length=1)
    failed_metrics: dict = Field(default_factory=dict)
    rejected_excerpt: str = Field(default="")
