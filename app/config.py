from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["anthropic", "openai"] = "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    x_bearer_token: str = ""

    # Comma-separated origins for CORS, or "*" for all (default).
    allowed_origins: str = "*"

    max_critic_retries: int = Field(default=3, ge=1, le=10)
    thread_min: int = Field(default=6, ge=1)
    thread_max: int = Field(default=9, ge=1)
    tweet_max_chars: int = 280

    min_thesis_confidence: float = Field(default=0.72, ge=0.0, le=1.0)
    min_input_worthiness_score: float = Field(default=0.45, ge=0.0, le=1.0)
    min_specificity_score: float = Field(default=0.35, ge=0.0, le=1.0)
    min_anchor_preservation_ratio: float = Field(default=0.5, ge=0.0, le=1.0)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def resolve_llm_provider(settings: Settings | None = None) -> Literal["anthropic", "openai"]:
    """Return the active provider and fail fast with a clear message if misconfigured."""
    settings = settings or get_settings()
    provider = settings.llm_provider
    has_anthropic = bool(settings.anthropic_api_key.strip())
    has_openai = bool(settings.openai_api_key.strip())

    if provider == "anthropic" and not has_anthropic:
        if has_openai:
            raise RuntimeError(
                "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is empty. "
                "Set LLM_PROVIDER=openai in .env (OpenAI key is present)."
            )
        raise RuntimeError(
            "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set in .env"
        )
    if provider == "openai" and not has_openai:
        if has_anthropic:
            raise RuntimeError(
                "LLM_PROVIDER=openai but OPENAI_API_KEY is empty. "
                "Set LLM_PROVIDER=anthropic in .env (Anthropic key is present)."
            )
        raise RuntimeError(
            "LLM_PROVIDER=openai but OPENAI_API_KEY is not set in .env"
        )
    return provider
