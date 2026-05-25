from typing import Any

from app.schemas.context import DistilledContext
from app.services.llm import invoke_structured


async def research_distiller_node(state: dict[str, Any]) -> dict[str, Any]:
    result = await invoke_structured(
        node_name="research_distiller",
        prompt_name="research",
        input_vars={
            "raw_context": state["raw_context"],
            "mode": state.get("selected_mode", "Contrarian VC"),
        },
        output_schema=DistilledContext,
    )
    log = list(state.get("pipeline_log", []))
    log.append("[Research] DONE")
    return {
        "distilled_context": result.model_dump(),
        "pipeline_log": log,
    }
