#!/usr/bin/env python3
"""Run benchmark checks and emit JSON report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.benchmarks.fixtures import ESSAY_CONTEXT, QRT_CONTEXT, STRONG_INPUT, WEAK_INPUT
from app.utils.input_worthiness import evaluate_input_worthiness
from app.utils.semantic_density import evaluate_semantic_density


def run_benchmarks() -> dict:
    weak_score = evaluate_input_worthiness(WEAK_INPUT).score
    strong_score = evaluate_input_worthiness(STRONG_INPUT).score
    qrt_semantic = evaluate_semantic_density(QRT_CONTEXT)
    essay_semantic = evaluate_semantic_density(ESSAY_CONTEXT)

    return {
        "refusal_precision": {
            "weak_input_worthiness": weak_score,
            "strong_input_worthiness": strong_score,
            "weak_should_refuse": weak_score < 0.45,
            "strong_should_pass_gate": strong_score >= 0.45,
        },
        "content_quality_signals": {
            "qrt_context_semantic_passed": qrt_semantic.passed,
            "essay_context_semantic_passed": essay_semantic.passed,
        },
        "summary": {
            "benchmarks_run": 4,
            "all_heuristics_passed": (
                weak_score < 0.45 and strong_score >= 0.45 and qrt_semantic.passed and essay_semantic.passed
            ),
        },
    }


if __name__ == "__main__":
    report = run_benchmarks()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["summary"]["all_heuristics_passed"] else 1)
