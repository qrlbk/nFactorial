from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.i18n import output_language_name
from app.services.llm import invoke_structured


class EssayOutput(BaseModel):
    title: str
    sections: list[str] = Field(min_length=3)
    markdown: str = Field(min_length=500)


async def essay_writer_node(state: dict[str, Any]) -> dict[str, Any]:
    result = await invoke_structured(
        node_name="essay_writer",
        prompt_name="essay_writer",
        input_vars={
            "mode": state.get("selected_mode", "Contrarian VC"),
            "output_language": state.get("output_language", "en"),
            "output_language_name": output_language_name(state.get("output_language", "en")),
            "thesis_position": state.get("thesis_position", {}),
            "distilled_context": state.get("distilled_context", {}),
            "narrative_frame": state.get("narrative_frame", {}),
            "retrieved_chunks": state.get("retrieved_chunks", []),
            "voice_guidelines": state.get("voice_guidelines", {}),
            "critic_feedback": (state.get("last_critic_report") or {}).get("verdict", "None"),
            "current_draft": state.get("current_draft", ""),
        },
        output_schema=EssayOutput,
    )
    sections = [s.strip() for s in result.sections if s.strip()]
    log = list(state.get("pipeline_log", []))
    log.append(f"[EssayWriter] DONE ({len(sections)} sections)")
    return {
        "essay_sections": sections,
        "current_draft": result.markdown,
        "current_tweets": sections,
        "pipeline_log": log,
    }
