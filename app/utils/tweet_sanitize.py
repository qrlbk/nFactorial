import re

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)
_LEADING_NUM = re.compile(
    r"^\s*(?:\d+\s*/\s*)+\d*\s*:?\s*",
    re.IGNORECASE,
)
_THREAD_PREFIX = re.compile(r"^\s*(?:tweet\s*)?\d+\s*[-–—]\s*", re.IGNORECASE)


def sanitize_tweet(text: str) -> str:
    cleaned = _EMOJI_PATTERN.sub("", text)
    cleaned = _LEADING_NUM.sub("", cleaned)
    cleaned = _THREAD_PREFIX.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def sanitize_tweets(tweets: list[str]) -> list[str]:
    return [sanitize_tweet(t) for t in tweets if sanitize_tweet(t)]
