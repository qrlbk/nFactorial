from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["arxiv", "hackernews", "substack", "twitter", "web"]


class DiscoveryItem(BaseModel):
    title: str
    url: str
    excerpt: str
    source_type: SourceType
    published_at: str | None = None
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    author: str | None = None


class DiscoveryResponse(BaseModel):
    query: str
    source: SourceType | str
    items: list[DiscoveryItem] = Field(default_factory=list)
    cached: bool = False


class IngestRequest(BaseModel):
    url: str = Field(min_length=8)
    title: str = ""


class IngestResponse(BaseModel):
    url: str
    title: str
    chunk_count: int
    preview: str
    chunks: list[dict] = Field(default_factory=list)


class ThesisCandidate(BaseModel):
    id: str
    hook: str
    defended_claim: str
    attacked_consensus: str
    intellectual_risk_level: int = Field(ge=8, le=10)
    thesis_confidence: float = Field(ge=0.0, le=1.0)


class ThesisAnglesResponse(BaseModel):
    trace_id: str | None = None
    candidates: list[ThesisCandidate] = Field(default_factory=list)
    distilled_context: dict = Field(default_factory=dict)


class VoiceProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    writing_samples: list[str] = Field(min_length=1)


class VoiceProfileItem(BaseModel):
    id: str
    name: str
    description: str
    guidelines: dict = Field(default_factory=dict)
    created_at: str


class VoiceListResponse(BaseModel):
    voices: list[VoiceProfileItem] = Field(default_factory=list)


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    chunk_count: int
    preview: str


class HookRequest(BaseModel):
    draft: str = Field(min_length=20)
    thesis: str = ""


class HookResponse(BaseModel):
    hooks: list[str] = Field(default_factory=list)


class LaunchDraftCreate(BaseModel):
    output_type: str = "thread"
    content: list[str] | str
    mode: str = "Contrarian VC"
    trace_id: str | None = None
    scheduled_at: datetime | None = None


class LaunchItem(BaseModel):
    id: str
    output_type: str
    content: list[str] | str
    mode: str
    trace_id: str | None = None
    status: str
    scheduled_at: str | None = None
    created_at: str


class LaunchListResponse(BaseModel):
    items: list[LaunchItem] = Field(default_factory=list)


class ResearchRunRequest(BaseModel):
    topic: str = Field(min_length=5)
    mode: str = "Contrarian VC"
    output_type: str = "thread"
    output_language: str = "en"
    auto_pick_thesis: bool = True
    source_urls: list[str] = Field(default_factory=list)


class ClaimVerification(BaseModel):
    claim: str
    status: Literal["supported", "unsupported", "hedged", "contradicted"]
    source_chunk_id: str | None = None
    source_url: str | None = None
    note: str = ""


class FactCheckReport(BaseModel):
    claims: list[ClaimVerification] = Field(default_factory=list)
    unsupported_ratio: float = 0.0
    passed: bool = True
