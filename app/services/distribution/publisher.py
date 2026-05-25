from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

from app.services.storage_paths import LAUNCH_QUEUE_DIR, ensure_data_dirs


class ContentPublisher(Protocol):
    async def publish(self, draft: dict[str, Any]) -> dict[str, Any]: ...
    async def schedule(self, draft: dict[str, Any], at: datetime) -> dict[str, Any]: ...


class MockXPublisher:
    async def publish(self, draft: dict[str, Any]) -> dict[str, Any]:
        draft = {**draft, "status": "published_mock", "published_at": datetime.now(timezone.utc).isoformat()}
        _save_draft(draft)
        return {"ok": True, "publisher": "mock_x", "draft_id": draft["id"], "message": "Saved to launch queue (mock publish)"}

    async def schedule(self, draft: dict[str, Any], at: datetime) -> dict[str, Any]:
        draft = {**draft, "status": "scheduled_mock", "scheduled_at": at.isoformat()}
        _save_draft(draft)
        return {"ok": True, "publisher": "mock_x", "draft_id": draft["id"], "scheduled_at": at.isoformat()}


class TwitterAPIPublisher:
    """Stub for future X API integration — set X_BEARER_TOKEN to enable."""

    def __init__(self, bearer_token: str = "") -> None:
        self.bearer_token = bearer_token

    async def publish(self, draft: dict[str, Any]) -> dict[str, Any]:
        if not self.bearer_token:
            return {"ok": False, "error": "X_BEARER_TOKEN not configured — use MockXPublisher"}
        draft = {**draft, "status": "published_stub"}
        _save_draft(draft)
        return {"ok": True, "publisher": "twitter_api_stub", "draft_id": draft["id"]}

    async def schedule(self, draft: dict[str, Any], at: datetime) -> dict[str, Any]:
        return {"ok": False, "error": "Scheduling requires X API — not yet implemented"}


def _save_draft(draft: dict[str, Any]) -> None:
    ensure_data_dirs()
    path = LAUNCH_QUEUE_DIR / f"{draft['id']}.json"
    path.write_text(json.dumps(draft, indent=2, default=str), encoding="utf-8")


def create_launch_draft(
    *,
    output_type: str,
    content: list[str] | str,
    mode: str,
    trace_id: str | None = None,
    scheduled_at: str | None = None,
) -> dict[str, Any]:
    draft_id = str(uuid.uuid4())[:12]
    payload = {
        "id": draft_id,
        "output_type": output_type,
        "content": content,
        "mode": mode,
        "trace_id": trace_id,
        "status": "queued",
        "scheduled_at": scheduled_at,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_draft(payload)
    return payload


def list_launch_queue(*, limit: int = 50) -> list[dict[str, Any]]:
    ensure_data_dirs()
    items: list[dict[str, Any]] = []
    for path in sorted(LAUNCH_QUEUE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            items.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
        if len(items) >= limit:
            break
    return items


def get_publisher(bearer_token: str = "") -> ContentPublisher:
    if bearer_token:
        return TwitterAPIPublisher(bearer_token)
    return MockXPublisher()
