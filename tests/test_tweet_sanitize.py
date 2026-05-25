from app.utils.tweet_sanitize import sanitize_tweet, sanitize_tweets


def test_sanitize_removes_emoji_and_numbering():
    raw = "1/ 1/9: GPU scarcity forces pricing up 🤔"
    assert sanitize_tweet(raw) == "GPU scarcity forces pricing up"


def test_sanitize_tweets_filters_empty():
    assert sanitize_tweets(["1/9: hello world", "   "]) == ["hello world"]
