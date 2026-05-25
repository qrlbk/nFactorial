"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { AppShell } from "@/components/AppShell";
import { fetchTraces } from "@/lib/api";
import { translateTraceStatus } from "@/lib/i18n-display";
import { DEFAULT_MODE_ID, type ModeId } from "@/lib/modes";
import type { TraceListItem } from "@/lib/types";

export default function HistoryPage() {
  const t = useTranslations("history");
  const [selectedModeId, setSelectedModeId] = useState<ModeId>(DEFAULT_MODE_ID);
  const [traces, setTraces] = useState<TraceListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTraces()
      .then((r) => setTraces(r.traces))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell selectedModeId={selectedModeId} onModeChange={setSelectedModeId}>
      <section className="p-6">
        <h1 className="mb-6 text-xl font-semibold">{t("title")}</h1>
        <article className="panel overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-[var(--border)] bg-[#0f1218] text-xs uppercase text-[var(--text-muted)]">
              <tr>
                <th className="px-4 py-3">{t("columns.date")}</th>
                <th className="px-4 py-3">{t("columns.mode")}</th>
                <th className="px-4 py-3">{t("columns.preview")}</th>
                <th className="px-4 py-3">{t("columns.status")}</th>
                <th className="px-4 py-3">{t("columns.retries")}</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-[var(--text-muted)]">
                    {t("loading")}
                  </td>
                </tr>
              ) : traces.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-[var(--text-muted)]">
                    {t("empty")}
                  </td>
                </tr>
              ) : (
                traces.map((row) => (
                  <tr key={row.trace_id} className="border-b border-[var(--border)]/50">
                    <td className="px-4 py-3 text-xs text-[var(--text-secondary)]">
                      {new Date(row.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">{row.mode}</td>
                    <td className="max-w-md truncate px-4 py-3 text-[var(--text-secondary)]">
                      {row.preview}
                    </td>
                    <td className="px-4 py-3">{translateTraceStatus(row.status, t)}</td>
                    <td className="px-4 py-3">{row.total_retries}</td>
                    <td className="px-4 py-3">
                      <Link href={`/traces/${row.trace_id}`} className="text-[var(--primary)] hover:underline">
                        {t("open")}
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </article>
      </section>
    </AppShell>
  );
}
