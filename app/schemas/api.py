from typing import Any, Literal

from pydantic import BaseModel, Field

SupportedLocale = Literal["en", "ru", "kk"]
SupportedOutputLanguage = Literal["en", "ru", "kk"]


class GenerateRequest(BaseModel):
    context: str = Field(min_length=50)
    mode: str = Field(default="Contrarian VC", min_length=1)
    output_language: SupportedOutputLanguage = "en"
    output_type: Literal["thread", "quote_retweet", "essay", "article"] = "thread"
    thesis_id: str | None = None
    voice_profile_id: str | None = None
    source_urls: list[str] = Field(default_factory=list)
    quoted_tweet: str = ""
    skip_post_pipeline: bool = False


class PipelineStepRecord(BaseModel):
    node: str
    status: str
    duration_ms: int = 0
    detail: str = ""


class ThreadStats(BaseModel):
    tweet_count: int = 0
    total_characters: int = 0
    signal_density: float = 0.0
    signal_density_label: str = "Low"
    mechanistic_layers: int = 0
    mechanistic_layers_target: int = 2
    epistemic_preserved: bool = False
    open_question_preserved: bool = False
    uncertainty_signals_kept: bool = False
    no_false_closure: bool = False


class GenerateResponse(BaseModel):
    final_thread: list[str] | None = None
    trace_id: str | None = None
    rejection_history: list[dict] = Field(default_factory=list)
    refused: bool = False
    refusal_reason: str | None = None
    pipeline_log: list[str] = Field(default_factory=list)
    pipeline_timeline: list[PipelineStepRecord] = Field(default_factory=list)
    thread_stats: ThreadStats | None = None
    key_insights: list[str] = Field(default_factory=list)
    total_retries: int = 0
    input_worthiness_score: float = 0.0
    output_type: str = "thread"
    thesis_candidates: list[dict] = Field(default_factory=list)
    final_output: dict = Field(default_factory=dict)
    hook_variants: list[str] = Field(default_factory=list)
    fact_check_report: dict = Field(default_factory=dict)


class TraceResponse(BaseModel):
    trace_id: str
    rejection_chain: list[dict] = Field(default_factory=list)
    cognition_stages: dict = Field(default_factory=dict)
    langfuse_url: str | None = None
    output_thread: list[str] | None = None
    refusal_reason: str | None = None
    input_preview: str = ""
    mode: str = ""
    total_retries: int = 0
    input_worthiness_score: float = 0.0
    pipeline_log: list[str] = Field(default_factory=list)
    pipeline_timeline: list[PipelineStepRecord] = Field(default_factory=list)
    thread_stats: ThreadStats | None = None
    key_insights: list[str] = Field(default_factory=list)
    status: str = "unknown"


class TraceListItem(BaseModel):
    trace_id: str
    created_at: str
    mode: str
    status: str
    preview: str
    tweet_count: int = 0
    total_retries: int = 0


class TraceListResponse(BaseModel):
    traces: list[TraceListItem] = Field(default_factory=list)
    total: int = 0


class EditorModePreset(BaseModel):
    id: str
    label: str
    description: str


class PublicConfigResponse(BaseModel):
    service_name: str = "Adversarial Editorial Engine"
    tracing_source: str = "local"
    editor_modes: list[EditorModePreset] = Field(default_factory=list)
    thresholds: dict = Field(default_factory=dict)


class TemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    context: str = Field(min_length=50)
    default_mode: str = Field(default="Contrarian VC")


class TemplateItem(BaseModel):
    id: str
    name: str
    description: str
    context: str
    default_mode: str
    created_at: str


class TemplateListResponse(BaseModel):
    templates: list[TemplateItem] = Field(default_factory=list)
