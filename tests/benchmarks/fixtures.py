"""Benchmark fixtures for evaluation pipeline."""

WEAK_INPUT = "AI is changing the world. Technology is amazing. The future is bright."

STRONG_INPUT = """
Hacker News discussion: "Why LLM inference costs won't follow Moore's Law"
Key points:
- GPT-4o full-context latency: 8s vs RAG pipeline: 1.2s at 500 docs
- Embedding refresh cost dominates when docs re-index weekly
- Eval harness quality is the moat, not base model choice
Open question: Will distillation close the gap before inference economics shift?
"""

QRT_CONTEXT = """
Quoted tweet: "RAG is solved — just use vector search + LLM."
Analysis: Production RAG at 500+ docs faces re-indexing costs, latency spikes during
embedding refresh, and eval regressions when chunk boundaries shift. Latency 8s full-context
vs 1.2s optimized RAG pipeline under load.
"""

ESSAY_CONTEXT = """
arXiv: Scaling laws for inference economics
The paper argues inference cost scales with memory bandwidth, not transistor density.
Batching improves throughput but increases tail latency for interactive apps.
Second-order effect: startups optimizing for demo latency vs production p99.
"""
