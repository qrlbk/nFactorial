"use client";

import { useTranslations } from "next-intl";
import type { PipelineStepRecord } from "@/lib/types";
import { formatSeconds, translatePipelineStatus } from "@/lib/i18n-display";

type Props = {
  timeline: PipelineStepRecord[];
  emptyLabel: string;
};

export function PipelineTimelineTable({ timeline, emptyLabel }: Props) {
  const t = useTranslations("journey.columns");
  const tSteps = useTranslations("pipeline.steps");
  const tPipeline = useTranslations("pipeline");
  const tCommon = useTranslations("common");

  if (timeline.length === 0) {
    return <p className="text-xs text-[var(--text-muted)]">{emptyLabel}</p>;
  }

  return (
    <section className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead>
          <tr className="border-b border-[var(--border)] text-[var(--text-muted)]">
            <th className="pb-2 pr-4 font-medium">{t("step")}</th>
            <th className="pb-2 pr-4 font-medium">{t("status")}</th>
            <th className="pb-2 pr-4 font-medium">{t("duration")}</th>
            <th className="pb-2 font-medium">{t("detail")}</th>
          </tr>
        </thead>
        <tbody>
          {timeline.map((row, i) => (
            <tr key={`${row.node}-${i}`} className="border-b border-[var(--border)]/50">
              <td className="py-2 pr-4">
                {tSteps(row.node as "context_qualification_gate")}
              </td>
              <td className="py-2 pr-4 uppercase">
                {translatePipelineStatus(row.status, tPipeline)}
              </td>
              <td className="py-2 pr-4">{formatSeconds(row.duration_ms, tCommon)}</td>
              <td className="py-2 text-[var(--text-secondary)]">{row.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
