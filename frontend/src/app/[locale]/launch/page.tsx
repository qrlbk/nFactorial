"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AppShell } from "@/components/AppShell";
import { fetchLaunchQueue } from "@/lib/api";
import type { LaunchItem } from "@/lib/platform-types";
import { DEFAULT_MODE_ID, type ModeId } from "@/lib/modes";

export default function LaunchPage() {
  const t = useTranslations("launch");
  const [modeId, setModeId] = useState<ModeId>(DEFAULT_MODE_ID);
  const [items, setItems] = useState<LaunchItem[]>([]);

  useEffect(() => {
    fetchLaunchQueue().then((r) => setItems(r.items)).catch(() => setItems([]));
  }, []);

  return (
    <AppShell selectedModeId={modeId} onModeChange={setModeId}>
      <div className="mx-auto max-w-4xl p-6">
        <h1 className="mb-2 text-2xl font-semibold">{t("title")}</h1>
        <p className="mb-6 text-sm text-[var(--text-muted)]">{t("subtitle")}</p>
        <div className="space-y-3">
          {items.map((item) => (
            <article key={item.id} className="rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] p-4">
              <div className="mb-1 flex justify-between text-sm"><span>{item.output_type}</span><span className="text-[var(--text-muted)]">{item.status}</span></div>
              <pre className="whitespace-pre-wrap text-xs">{typeof item.content === "string" ? item.content : item.content.join("\n\n")}</pre>
            </article>
          ))}
          {!items.length && <p className="text-sm text-[var(--text-muted)]">{t("empty")}</p>}
        </div>
      </div>
    </AppShell>
  );
}
