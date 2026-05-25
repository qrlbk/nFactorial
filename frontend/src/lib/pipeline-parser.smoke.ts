import { buildPipelineSteps } from "./pipeline-parser";
import type { PipelineStepRecord } from "./types";

const timeline: PipelineStepRecord[] = [
  { node: "context_qualification_gate", status: "qualified", duration_ms: 600, detail: "score 1.0" },
  { node: "deterministic_evaluators", status: "rejected", duration_ms: 120, detail: "specificity low" },
  { node: "deterministic_evaluators", status: "passed", duration_ms: 90, detail: "passed" },
];

const steps = buildPipelineSteps(timeline, [
  {
    node: "deterministic_evaluators",
    timestamp: "",
    reason: "Specificity score 0.29 below 0.35",
    failed_metrics: {},
    rejected_excerpt: "",
  },
]);

if (steps.length !== 3) {
  throw new Error(`Expected 3 steps, got ${steps.length}`);
}
if (steps[1].status !== "rejected") {
  throw new Error("Expected rejected status on evaluators");
}

console.log("pipeline-parser smoke test passed");
