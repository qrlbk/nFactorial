from typing import Any

from app.i18n import output_language_name
from app.schemas.narrative import NarrativeFrame
from app.services.llm import invoke_structured


async def narrative_architect_node(state: dict[str, Any]) -> dict[str, Any]:
    result = await invoke_structured(
        node_name="narrative_architect",
        prompt_name="narrative",
        input_vars={
            "mode": state.get("selected_mode", "Contrarian VC"),
            "output_language": state.get("output_language", "en"),
            "output_language_name": output_language_name(state.get("output_language", "en")),
            "thesis_position": state["thesis_position"],
            "distilled_context": state["distilled_context"],
        },
        output_schema=NarrativeFrame,
    )
    log = list(state.get("pipeline_log", []))
    log.append("[Narrative] DONE")
    return {
        "narrative_frame": result.model_dump(),
        "narrative_completed": True,
        "pipeline_log": log,
    }
