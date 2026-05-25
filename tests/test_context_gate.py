import pytest

from app.graph.nodes.context_gate import context_qualification_gate_node
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_context_gate_node_refuses_weak_paste():
    raw = (FIXTURES / "human_paste_weak.txt").read_text(encoding="utf-8")
    result = await context_qualification_gate_node({"raw_context": raw, "pipeline_log": [], "rejection_history": []})
    assert result["context_qualified"] is False
    assert "Generation refused" in result["refusal_reason"]
    assert any("[Context Gate] REFUSED" in line for line in result["pipeline_log"])
