from __future__ import annotations

from typing import Any

from app.graph.nodes.essay_writer import essay_writer_node
from app.graph.nodes.qrt_writer import qrt_writer_node
from app.graph.nodes.rewrite import high_pressure_rewriter_node


async def writer_dispatch_node(state: dict[str, Any]) -> dict[str, Any]:
    output_type = state.get("output_type", "thread")
    if output_type == "quote_retweet":
        return await qrt_writer_node(state)
    if output_type in ("essay", "article"):
        return await essay_writer_node(state)
    return await high_pressure_rewriter_node(state)
