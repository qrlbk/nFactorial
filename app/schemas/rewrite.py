from pydantic import BaseModel, Field, field_validator

from app.config import get_settings


class RewriteOutput(BaseModel):
    tweets: list[str] = Field(min_length=1)

    @field_validator("tweets")
    @classmethod
    def validate_tweet_lengths(cls, v: list[str]) -> list[str]:
        settings = get_settings()
        for i, tweet in enumerate(v):
            if len(tweet) > settings.tweet_max_chars:
                raise ValueError(f"Tweet {i + 1} exceeds {settings.tweet_max_chars} chars")
            if not tweet.strip():
                raise ValueError(f"Tweet {i + 1} is empty")
        return v
