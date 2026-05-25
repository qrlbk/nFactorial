from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.services.llm import invoke_structured


class HookOutput(BaseModel):
    hooks: list[str] = Field(min_length=3, max_length=5)


async def hook_generator_node(state: dict[str, Any]) -> dict[str, Any]:
    draft = state.get("current_draft") or "\n".join(state.get("current_tweets") or [])
    result = await invoke_structured(
        node_name="hook_generator",
        prompt_name="hooks",
        input_vars={
            "draft": draft,
            "thesis_position": state.get("thesis_position", {}),
            "output_language": state.get("output_language", "en"),
        },
        output_schema=HookOutput,
    )
    log = list(state.get("pipeline_log", []))
    log.append("[Hooks] DONE")
    return {"hook_variants": result.hooks, "pipeline_log": log}


async def generate_hooks_for_draft(draft: str, *, thesis: str = "", output_language: str = "en") -> list[str]:
    result = await invoke_structured(
        node_name="hook_generator",
        prompt_name="hooks",
        input_vars={"draft": draft, "thesis_position": {"defended_claim": thesis}, "output_language": output_language},
        output_schema=HookOutput,
    )
    return result.hooks
