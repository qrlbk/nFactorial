from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.llm import invoke_structured
from app.services.storage_paths import VOICES_DIR, ensure_data_dirs
from pydantic import BaseModel, Field


class VoiceGuidelines(BaseModel):
    sentence_rhythm: str = ""
    opinion_strength: str = ""
    vocabulary_notes: str = ""
    taboo_phrases: list[str] = Field(default_factory=list)
    reference_writers: list[str] = Field(default_factory=list)
    sample_excerpt: str = ""


class VoiceProfileOutput(BaseModel):
    guidelines: VoiceGuidelines


def _voice_path(voice_id: str) -> Path:
    ensure_data_dirs()
    return VOICES_DIR / f"{voice_id}.json"


def list_voices() -> list[dict[str, Any]]:
    ensure_data_dirs()
    items: list[dict[str, Any]] = []
    for path in sorted(VOICES_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append(
                {
                    "id": data["id"],
                    "name": data["name"],
                    "description": data.get("description", ""),
                    "guidelines": data.get("guidelines", {}),
                    "created_at": data.get("created_at", ""),
                }
            )
        except (json.JSONDecodeError, KeyError):
            continue
    return items


def get_voice(voice_id: str) -> dict[str, Any] | None:
    path = _voice_path(voice_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


async def create_voice_profile(
    *,
    name: str,
    description: str,
    writing_samples: list[str],
) -> dict[str, Any]:
    combined = "\n\n---\n\n".join(s.strip() for s in writing_samples if s.strip())
    result = await invoke_structured(
        node_name="voice_profiler",
        prompt_name="voice_profiler",
        input_vars={"writing_samples": combined[:12000]},
        output_schema=VoiceProfileOutput,
    )
    voice_id = str(uuid.uuid4())[:12]
    payload = {
        "id": voice_id,
        "name": name,
        "description": description,
        "guidelines": result.guidelines.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _voice_path(voice_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def delete_voice(voice_id: str) -> bool:
    path = _voice_path(voice_id)
    if not path.exists():
        return False
    path.unlink()
    return True
