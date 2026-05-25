from typing import Any, Literal, TypedDict

OutputType = Literal["thread", "quote_retweet", "essay", "article"]


class EditorialState(TypedDict, total=False):
    raw_context: str
    selected_mode: str
    output_type: OutputType
    quoted_tweet: str
    distilled_context: dict[str, Any]
    thesis_position: dict[str, Any]
    thesis_candidates: list[dict[str, Any]]
    selected_thesis_id: str | None
    thesis_only: bool
    narrative_frame: dict[str, Any]
    current_draft: str
    current_tweets: list[str]
    essay_sections: list[str]
    last_critic_report: dict[str, Any]
    rejection_history: list[dict[str, Any]]
    critic_attempts: int
    rewrite_attempts: int
    total_retry_count: int
    final_elite_thread: list[str]
    final_output: dict[str, Any]
    refusal_reason: str | None
    trace_id: str | None
    pipeline_log: list[str]
    pipeline_timeline: list[dict[str, Any]]
    eval_passed: bool
    narrative_completed: bool
    context_qualified: bool
    input_worthiness_score: float
    borderline_input: bool
    critic_strictness_boost: float
    output_language: str
    response_locale: str
    source_urls: list[str]
    source_documents: list[dict[str, Any]]
    retrieved_chunks: list[dict[str, Any]]
    voice_profile_id: str | None
    voice_guidelines: dict[str, Any]
    fact_check_report: dict[str, Any]
    hook_variants: list[str]
    skip_post_pipeline: bool
    autonomous_research: bool
    research_topic: str | None
