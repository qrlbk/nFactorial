"use client";

import { useTranslations } from "next-intl";
import type { PipelineStepUI } from "@/lib/types";
import { PIPELINE_STEP_KEYS } from "@/lib/pipeline-parser";

type Props = {
  steps: PipelineStepUI[];
  visibleCount: number;
  loading?: boolean;
  runningIndex?: number;
};

export function CognitivePipelineStepper({
  steps,
  visibleCount,
  loading,
  runningIndex,
}: Props) {
  const t = useTranslations("pipeline");
  const tCommon = useTranslations("common");

  const displaySteps: PipelineStepUI[] =
    steps.length > 0
      ? steps.slice(0, visibleCount)
      : loading && runningIndex !== undefined
        ? Array.from({ length: runningIndex + 1 }, (_, i) => ({
            id: `skeleton-${i}`,
            label: t(`steps.${PIPELINE_STEP_KEYS[i]}` as "steps.context_qualification_gate"),
            status: (i === runningIndex
              ? "running"
              : i < runningIndex
                ? "done"
                : "pending") as PipelineStepUI["status"],
          }))
        : [];

  const statusLabel = (status: PipelineStepUI["status"]) =>
    t(`status.${status}` as "status.done");

  return (
    <article className="panel flex h-full flex-col p-4">
      <header className="mb-4 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
        {t("title")}
      </header>
      <section className="space-y-0 overflow-y-auto pr-1">
        {displaySteps.map((step, index) => (
          <section key={step.id} className="relative flex gap-3 pb-5">
            {index < displaySteps.length - 1 && (
              <span className="absolute left-[11px] top-6 h-[calc(100%-8px)] w-px bg-[var(--border)]" />
            )}
            <span
              className={`relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ${
                step.status === "rejected" || step.status === "refused"
                  ? "bg-[var(--danger)]/20 text-[var(--danger)]"
                  : step.status === "running"
                    ? "bg-[var(--primary)]/20 text-[var(--primary)]"
                    : "bg-[var(--success)]/15 text-[var(--success)]"
              }`}
            >
              {index + 1}
            </span>
            <section className="min-w-0 flex-1">
              <section className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-medium">{step.label}</span>
                <span className="status-pill bg-[var(--border)] text-[var(--text-muted)]">
                  {statusLabel(step.status)}
                </span>
                {step.durationMs ? (
                  <span className="text-xs text-[var(--text-muted)]">
                    {tCommon("seconds", { n: (step.durationMs / 1000).toFixed(1) })}
                  </span>
                ) : null}
              </section>
              {step.detail ? (
                <p className="mt-1 text-xs text-[var(--text-secondary)]">{step.detail}</p>
              ) : null}
              {step.reason && step.status === "rejected" ? (
                <section className="mt-2 rounded-lg border border-[var(--danger)]/30 bg-[var(--danger)]/10 p-3">
                  <header className="mb-1 flex flex-wrap items-center gap-2 text-[10px] font-semibold uppercase text-[var(--danger)]">
                    <span>{t("reason")}</span>
                    <span className="rounded bg-[var(--danger)]/20 px-1.5 py-0.5 normal-case">
                      {tCommon("originalEvaluatorNote")}
                    </span>
                  </header>
                  <p className="text-xs text-[var(--danger)]/90">{step.reason}</p>
                </section>
              ) : null}
            </section>
          </section>
        ))}
      </section>
    </article>
  );
}
