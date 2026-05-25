from __future__ import annotations

from typing import Any

from app.schemas.platform import ClaimVerification, FactCheckReport
from app.services.llm import invoke_structured
from pydantic import BaseModel, Field


class FactCheckLLMOutput(BaseModel):
    claims: list[ClaimVerification] = Field(default_factory=list)


async def fact_checker_node(state: dict[str, Any]) -> dict[str, Any]:
    draft = state.get("current_draft") or "\n".join(state.get("current_tweets") or [])
    chunks = state.get("retrieved_chunks") or []
    if not draft.strip():
        return {"fact_check_report": FactCheckReport().model_dump()}

    result = await invoke_structured(
        node_name="fact_checker",
        prompt_name="fact_checker",
        input_vars={
            "draft": draft,
            "retrieved_chunks": chunks,
            "distilled_context": state.get("distilled_context", {}),
        },
        output_schema=FactCheckLLMOutput,
    )
    claims = result.claims
    unsupported = sum(1 for c in claims if c.status in ("unsupported", "contradicted"))
    ratio = unsupported / len(claims) if claims else 0.0
    report = FactCheckReport(
        claims=claims,
        unsupported_ratio=round(ratio, 3),
        passed=ratio < 0.15,
    )
    log = list(state.get("pipeline_log", []))
    log.append(f"[FactCheck] {'PASSED' if report.passed else 'FAILED'} ({len(claims)} claims)")
    return {"fact_check_report": report.model_dump(), "pipeline_log": log}
