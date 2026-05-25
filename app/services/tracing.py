from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

from langfuse import Langfuse

from app.config import get_settings
from app.services.local_trace import LocalTrace, create_local_trace, fetch_local_trace

_langfuse: Langfuse | None = None


def get_langfuse() -> Langfuse | None:
    global _langfuse
    settings = get_settings()
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return None
    if _langfuse is None:
        _langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    return _langfuse


@contextmanager
def editorial_trace(
    *,
    context_preview: str,
    mode: str,
) -> Generator[tuple[Any, str], None, None]:
    client = get_langfuse()
    if client is not None:
        trace = client.trace(
            name="adversarial-editorial-run",
            input={"context_preview": context_preview[:500], "mode": mode},
            metadata={"product": "adversarial-editorial-engine", "source": "langfuse"},
        )
        try:
            yield trace, trace.id
        finally:
            client.flush()
        return

    local = create_local_trace(context_preview=context_preview, mode=mode)
    try:
        yield local, local.id
    finally:
        local.save()


def log_rejection(
    trace: Any,
    *,
    node: str,
    reason: str,
    failed_metrics: dict,
    rejected_excerpt: str,
    retry_count: int,
) -> None:
    payload = {
        "node": node,
        "reason": reason,
        "failed_metrics": failed_metrics,
        "rejected_excerpt": rejected_excerpt[:500],
        "retry_count": retry_count,
    }
    if trace is None:
        return
    if isinstance(trace, LocalTrace):
        trace.event(name="rejection", metadata=payload)
        trace.score(name=f"rejection_{node}", value=0, comment=reason)
        return
    trace.event(name="rejection", metadata=payload)
    trace.score(name=f"rejection_{node}", value=0, comment=reason)


def finalize_trace(
    trace: Any,
    *,
    output: dict,
    metadata: dict | None = None,
) -> None:
    if trace is None:
        return
    trace.update(output=output, metadata=metadata or {})
    if isinstance(trace, LocalTrace):
        trace.save()
        return
    client = get_langfuse()
    if client:
        client.flush()


def fetch_trace_summary(trace_id: str) -> dict:
    local = fetch_local_trace(trace_id)
    if "error" not in local:
        return local

    client = get_langfuse()
    if client is None:
        return {"trace_id": trace_id, "error": "Trace not found"}
    try:
        trace = client.fetch_trace(trace_id)
        return trace.dict() if hasattr(trace, "dict") else {"trace_id": trace_id, "data": str(trace)}
    except Exception as e:
        return {"trace_id": trace_id, "error": str(e)}
