"use client";

import { useTranslations } from "next-intl";
import { RejectionChart } from "./RejectionChart";
import { PipelineTimelineTable } from "./PipelineTimelineTable";
import { InsightPills } from "./InsightPills";
import type { PipelineStepRecord, RejectionEvent } from "@/lib/types";

type Props = {
  rejections: RejectionEvent[];
  timeline: PipelineStepRecord[];
  insights: string[];
};

export function CognitiveJourneyPanel({ rejections, timeline, insights }: Props) {
  const t = useTranslations("journey");

  return (
    <article className="panel mt-6 p-5">
      <header className="mb-4 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
        {t("title")}
      </header>
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section>
          <header className="mb-2 text-xs font-medium text-[var(--text-secondary)]">
            {t("rejectionHistory")}
          </header>
          <RejectionChart
            rejections={rejections}
            emptyLabel={t("noRejections")}
            attemptLabel={(n) => t("attemptLabel", { n })}
          />
        </section>
        <section>
          <header className="mb-2 text-xs font-medium text-[var(--text-secondary)]">{t("timeline")}</header>
          <PipelineTimelineTable timeline={timeline} emptyLabel={t("noTimeline")} />
        </section>
        <section>
          <header className="mb-2 text-xs font-medium text-[var(--text-secondary)]">
            {t("keyInsights")}
          </header>
          <InsightPills insights={insights} emptyLabel={t("noInsights")} />
        </section>
      </section>
    </article>
  );
}
