from __future__ import annotations

from app.schemas.platform import DiscoveryItem

# Mock curated viral tweets — replace with X API when keys available
_MOCK_TWEETS: list[dict[str, str]] = [
    {
        "title": "LLM inference cost curve",
        "url": "https://x.com/mock/status/1",
        "excerpt": "Everyone thinks inference follows Moore's Law. It doesn't — batching economics and memory bandwidth dominate.",
        "author": "mock_analyst",
    },
    {
        "title": "RAG is not retrieval",
        "url": "https://x.com/mock/status/2",
        "excerpt": "RAG pipelines optimize recall. Production systems optimize latency under constraint. Different game.",
        "author": "mock_engineer",
    },
    {
        "title": "Eval harness moat",
        "url": "https://x.com/mock/status/3",
        "excerpt": "The moat in AI apps isn't the model — it's the eval loop that catches regressions your users feel first.",
        "author": "mock_founder",
    },
    {
        "title": "Agent hype cycle",
        "url": "https://x.com/mock/status/4",
        "excerpt": "Agents work when the action space is narrow and verifiable. They fail when success is subjective.",
        "author": "mock_researcher",
    },
    {
        "title": "Foundation model commoditization",
        "url": "https://x.com/mock/status/5",
        "excerpt": "Base model quality is converging. Distribution and workflow lock-in are where margin lives now.",
        "author": "mock_vc",
    },
]


def trending_tweets(topic: str, *, max_results: int = 10) -> list[DiscoveryItem]:
    q = topic.lower()
    items: list[DiscoveryItem] = []
    for idx, tweet in enumerate(_MOCK_TWEETS):
        blob = f"{tweet['title']} {tweet['excerpt']}".lower()
        score = 0.9 - idx * 0.05
        if q in blob or any(tok in blob for tok in q.split() if len(tok) > 3):
            score += 0.05
        items.append(
            DiscoveryItem(
                title=tweet["title"],
                url=tweet["url"],
                excerpt=tweet["excerpt"],
                source_type="twitter",
                relevance_score=min(1.0, score),
                author=tweet.get("author"),
            )
        )
    items.sort(key=lambda x: x.relevance_score, reverse=True)
    return items[:max_results]
