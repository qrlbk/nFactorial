#!/usr/bin/env python3
"""CLI entry point for the adversarial editorial pipeline."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.graph.builder import run_pipeline


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Adversarial Editorial Engine — transform context into elite threads"
    )
    parser.add_argument("input_file", type=Path, help="Path to context text file")
    parser.add_argument(
        "--mode",
        default="Contrarian VC",
        help="Editorial mode (default: Contrarian VC)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    args = parser.parse_args()

    if not args.input_file.exists():
        print(f"Error: file not found: {args.input_file}", file=sys.stderr)
        return 1

    context = args.input_file.read_text(encoding="utf-8")
    if len(context.strip()) < 50:
        print("Error: context must be at least 50 characters", file=sys.stderr)
        return 1

    result = asyncio.run(run_pipeline(raw_context=context, mode=args.mode))

    if args.json:
        print(
            json.dumps(
                {
                    "final_thread": result.get("final_elite_thread"),
                    "trace_id": result.get("trace_id"),
                    "rejection_history": result.get("rejection_history", []),
                    "refused": bool(result.get("refusal_reason")),
                    "refusal_reason": result.get("refusal_reason"),
                    "pipeline_log": result.get("pipeline_log", []),
                },
                indent=2,
                default=str,
            )
        )
    else:
        for line in result.get("pipeline_log", []):
            print(line)
        print()
        if result.get("final_elite_thread"):
            print("=== ELITE THREAD ===")
            for i, tweet in enumerate(result["final_elite_thread"], 1):
                print(f"\n{i}/ {tweet}")
            if result.get("trace_id"):
                print(f"\nTrace ID: {result['trace_id']}")
        else:
            print(result.get("refusal_reason", "Generation failed."))
            if result.get("trace_id"):
                print(f"Trace ID: {result['trace_id']}")

    return 0 if result.get("final_elite_thread") else 1


if __name__ == "__main__":
    sys.exit(main())
