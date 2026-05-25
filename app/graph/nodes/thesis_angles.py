from __future__ import annotations

import uuid
from typing import Any

from app.schemas.platform import ThesisCandidate
from app.schemas.thesis import ThesisPosition
from app.services.llm import invoke_structured
from pydantic import BaseModel, Field


class ThesisAnglesOutput(BaseModel):
    candidates: list[ThesisCandidate] = Field(min_length=1, max_length=5)


async def thesis_angles_node(state: dict[str, Any]) -> dict[str, Any]:
    result = await invoke_structured(
        node_name="thesis_angles_generator",
        prompt_name="thesis_angles",
        input_vars={
            "distilled_context": state.get("distilled_context", {}),
            "mode": state.get("selected_mode", "Contrarian VC"),
        },
        output_schema=ThesisAnglesOutput,
    )
    candidates = []
    for cand in result.candidates:
        data = cand.model_dump()
        if not data.get("id"):
            data["id"] = str(uuid.uuid4())[:8]
        candidates.append(data)

    log = list(state.get("pipeline_log", []))
    log.append(f"[ThesisAngles] DONE ({len(candidates)} candidates)")

    update: dict[str, Any] = {
        "thesis_candidates": candidates,
        "pipeline_log": log,
    }

    selected_id = state.get("selected_thesis_id")
    thesis_only = state.get("thesis_only", False)
    if selected_id:
        picked = next((c for c in candidates if c["id"] == selected_id), None)
        if picked:
            thesis = ThesisPosition(
                attacked_consensus=picked["attacked_consensus"],
                defended_claim=picked["defended_claim"],
                strongest_counterargument="Strongest counter: consensus has institutional inertia",
                why_counterargument_fails="Counter fails because operational metrics contradict narrative",
                intellectual_risk_level=picked["intellectual_risk_level"],
                thesis_confidence=picked["thesis_confidence"],
            )
            update["thesis_position"] = thesis.model_dump()
            update["current_draft"] = f"THESIS: {picked['defended_claim']}\nHOOK: {picked['hook']}"
    elif thesis_only:
        update["final_output"] = {"thesis_candidates": candidates}

    return update
