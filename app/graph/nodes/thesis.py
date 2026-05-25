from typing import Any

from app.config import get_settings
from app.graph.refusal_messages import THESIS_CONFIDENCE_REFUSAL
from app.schemas.thesis import ThesisPosition
from app.services.llm import invoke_structured


async def thesis_commitment_node(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("thesis_position"):
        log = list(state.get("pipeline_log", []))
        log.append("[Thesis] SKIPPED (pre-selected)")
        return {"pipeline_log": log}

    settings = get_settings()
    result = await invoke_structured(
        node_name="thesis_commitment",
        prompt_name="thesis",
        input_vars={"distilled_context": state["distilled_context"]},
        output_schema=ThesisPosition,
    )

    log = list(state.get("pipeline_log", []))
    log.append("[Thesis] DONE")

    if result.thesis_confidence < settings.min_thesis_confidence:
        log.append(
            f"[Thesis] REFUSED (confidence={result.thesis_confidence:.2f} "
            f"< {settings.min_thesis_confidence})"
        )
        return {
            "thesis_position": result.model_dump(),
            "refusal_reason": THESIS_CONFIDENCE_REFUSAL,
            "pipeline_log": log,
        }

    thesis = result.model_dump()
    draft_stub = (
        f"THESIS: {thesis['defended_claim']}\n"
        f"ATTACKING: {thesis['attacked_consensus']}\n"
        f"CONFIDENCE: {thesis['thesis_confidence']}\n"
        f"RISK LEVEL: {thesis['intellectual_risk_level']}"
    )
    return {
        "thesis_position": thesis,
        "current_draft": draft_stub,
        "pipeline_log": log,
    }
