import type { PipelineStepRecord, PipelineStepUI, RejectionEvent } from "./types";

export function formatRetryLabel(
  attempt: number,
  t?: (key: string, values: Record<string, number>) => string,
): string {
  if (t) {
    return t("pipeline.retryLabel", { attempt });
  }
  return `#${attempt}`;
}

export function buildPipelineSteps(
  timeline: PipelineStepRecord[],
  rejections: RejectionEvent[] = [],
  translateStep: (node: string) => string = (node) => node,
  formatRetry?: (attempt: number) => string,
): PipelineStepUI[] {
  const steps: PipelineStepUI[] = [];
  const rewriteCount: Record<string, number> = {};

  for (const entry of timeline) {
    const label = translateStep(entry.node);
    let retryLabel: string | undefined;
    if (entry.node === "high_pressure_rewriter") {
      rewriteCount[entry.node] = (rewriteCount[entry.node] || 0) + 1;
      if (rewriteCount[entry.node] > 1) {
        const attempt = rewriteCount[entry.node] - 1;
        retryLabel = formatRetry ? formatRetry(attempt) : `#${attempt}`;
      }
    }

    steps.push({
      id: `${entry.node}-${steps.length}`,
      label: retryLabel ? `${label} (${retryLabel})` : label,
      status: mapStatus(entry.status),
      durationMs: entry.duration_ms,
      detail: entry.detail,
      reason:
        entry.status === "rejected" || entry.status === "refused"
          ? findRejectionReason(entry.node, rejections) || entry.detail
          : undefined,
      retryLabel,
    });
  }

  return steps;
}

function mapStatus(status: string): PipelineStepUI["status"] {
  const normalized = status.toLowerCase();
  if (
    ["done", "qualified", "borderline", "passed", "approved", "retry"].includes(
      normalized,
    )
  ) {
    return normalized as PipelineStepUI["status"];
  }
  if (normalized === "refused" || normalized === "fail_closed") {
    return normalized as PipelineStepUI["status"];
  }
  if (normalized === "rejected") return "rejected";
  return "done";
}

function findRejectionReason(
  node: string,
  rejections: RejectionEvent[],
): string | undefined {
  const match = [...rejections].reverse().find((r) => r.node === node);
  return match?.reason;
}

export function heuristicRunningStep(elapsedMs: number): number {
  const thresholds = [800, 4000, 7000, 10000, 14000, 18000, 22000, 26000];
  for (let i = 0; i < thresholds.length; i += 1) {
    if (elapsedMs < thresholds[i]) return i;
  }
  return thresholds.length - 1;
}

export const PIPELINE_STEP_KEYS = [
  "context_qualification_gate",
  "retrieval_agent",
  "research_distiller",
  "thesis_angles_generator",
  "thesis_commitment",
  "narrative_architect",
  "high_pressure_rewriter",
  "deterministic_evaluators",
  "anti_slop_critic",
  "fact_checker",
  "hook_generator",
  "distribution_agent",
  "thread_assembler",
] as const;
