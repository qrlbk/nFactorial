from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRACE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "traces"
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "templates"


class LocalTrace:
    """File-backed trace when Langfuse is not configured."""

    def __init__(self, trace_id: str, *, context_preview: str, mode: str) -> None:
        self.id = trace_id
        self._data: dict[str, Any] = {
            "trace_id": trace_id,
            "name": "adversarial-editorial-run",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "input": {"context_preview": context_preview[:500], "mode": mode},
            "output": None,
            "metadata": {"product": "adversarial-editorial-engine", "source": "local"},
            "events": [],
            "scores": [],
        }

    def event(self, *, name: str, metadata: dict) -> None:
        self._data["events"].append(
            {"name": name, "metadata": metadata, "timestamp": datetime.now(timezone.utc).isoformat()}
        )

    def score(self, *, name: str, value: float, comment: str = "") -> None:
        self._data["scores"].append({"name": name, "value": value, "comment": comment})

    def update(self, *, output: dict, metadata: dict | None = None) -> None:
        self._data["output"] = output
        if metadata:
            self._data["metadata"].update(metadata)

    def save(self) -> None:
        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        path = TRACE_DIR / f"{self.id}.json"
        path.write_text(json.dumps(self._data, indent=2, default=str), encoding="utf-8")


def create_local_trace(*, context_preview: str, mode: str) -> LocalTrace:
    return LocalTrace(str(uuid.uuid4()), context_preview=context_preview, mode=mode)


def fetch_local_trace(trace_id: str) -> dict[str, Any]:
    path = TRACE_DIR / f"{trace_id}.json"
    if not path.exists():
        return {"trace_id": trace_id, "error": "Trace not found"}
    return json.loads(path.read_text(encoding="utf-8"))


def _trace_status(data: dict[str, Any]) -> str:
    output = data.get("output") or {}
    if output.get("thread"):
        return "success"
    return "refused"


def list_local_traces(*, limit: int = 50, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(TRACE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    total = len(files)
    items: list[dict[str, Any]] = []

    for path in files[offset : offset + limit]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        metadata = data.get("metadata") or {}
        inp = data.get("input") or {}
        output = data.get("output") or {}
        thread = output.get("thread") or []

        items.append(
            {
                "trace_id": data.get("trace_id", path.stem),
                "created_at": data.get("created_at", ""),
                "mode": inp.get("mode", ""),
                "status": _trace_status(data),
                "preview": inp.get("context_preview", "")[:160],
                "tweet_count": len(thread),
                "total_retries": int(metadata.get("total_retries") or 0),
            }
        )

    return items, total


def list_templates() -> list[dict[str, Any]]:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, Any]] = []
    for path in sorted(TEMPLATE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return items


def create_template(*, name: str, description: str, context: str, default_mode: str) -> dict[str, Any]:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    template_id = str(uuid.uuid4())
    payload = {
        "id": template_id,
        "name": name,
        "description": description,
        "context": context,
        "default_mode": default_mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = TEMPLATE_DIR / f"{template_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def delete_template(template_id: str) -> bool:
    path = TEMPLATE_DIR / f"{template_id}.json"
    if not path.exists():
        return False
    path.unlink()
    return True
