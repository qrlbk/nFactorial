"use client";

import { useTranslations } from "next-intl";
import type { ThreadStats } from "@/lib/types";
import { CheckCircle2 } from "lucide-react";

type Props = {
  stats: ThreadStats | null;
};

export function ThreadStatsPanel({ stats }: Props) {
  const t = useTranslations("stats");
  if (!stats) return null;

  return (
    <section className="mt-4 rounded-lg border border-[var(--primary)]/30 bg-[var(--primary)]/5 p-4">
      <header className="mb-3 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
        {t("title")}
      </header>
      <section className="grid grid-cols-2 gap-3 text-sm">
        <Stat label={t("tweets")} value={String(stats.tweet_count)} />
        <Stat label={t("characters")} value={String(stats.total_characters)} />
        <Stat
          label={t("signalDensity")}
          value={`${stats.signal_density} (${stats.signal_density_label})`}
        />
        <Stat
          label={t("mechanisticLayers")}
          value={`${stats.mechanistic_layers}/${stats.mechanistic_layers_target}`}
          ok={stats.mechanistic_layers >= stats.mechanistic_layers_target}
        />
        <Stat
          label={t("epistemicStatus")}
          value={stats.epistemic_preserved ? t("preserved") : t("degraded")}
          ok={stats.epistemic_preserved}
        />
      </section>
      <section className="mt-3 flex flex-wrap gap-2 text-[10px] text-[var(--text-muted)]">
        {stats.open_question_preserved && <Badge>{t("badges.openQuestion")}</Badge>}
        {stats.uncertainty_signals_kept && <Badge>{t("badges.uncertainty")}</Badge>}
        {stats.no_false_closure && <Badge>{t("badges.noClosure")}</Badge>}
      </section>
    </section>
  );
}

function Stat({ label, value, ok }: { label: string; value: string; ok?: boolean }) {
  return (
    <section>
      <span className="text-xs text-[var(--text-muted)]">{label}</span>
      <section className="flex items-center gap-1 font-medium">
        {ok ? <CheckCircle2 className="h-3.5 w-3.5 text-[var(--success)]" /> : null}
        {value}
      </section>
    </section>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-full border border-[var(--border)] bg-[var(--bg-panel)] px-2 py-0.5">
      {children}
    </span>
  );
}
