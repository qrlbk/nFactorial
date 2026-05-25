"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { AppShell } from "@/components/AppShell";
import { discoverContent } from "@/lib/api";
import type { DiscoveryItem } from "@/lib/platform-types";
import { DEFAULT_MODE_ID, type ModeId } from "@/lib/modes";
import { Loader2, Search } from "lucide-react";

const SOURCES = ["arxiv", "hackernews", "substack", "tweets"] as const;

export default function DiscoverPage() {
  const t = useTranslations("discover");
  const router = useRouter();
  const [modeId, setModeId] = useState<ModeId>(DEFAULT_MODE_ID);
  const [query, setQuery] = useState("LLM inference");
  const [source, setSource] = useState<(typeof SOURCES)[number]>("arxiv");
  const [items, setItems] = useState<DiscoveryItem[]>([]);
  const [loading, setLoading] = useState(false);

  async function search() {
    setLoading(true);
    try {
      const res = await discoverContent(source, query);
      setItems(res.items);
    } finally {
      setLoading(false);
    }
  }

  function openWithContext(item: DiscoveryItem) {
    const ctx = `${item.title}\n\n${item.excerpt}\n\nSource: ${item.url}`;
    router.push(`/?context=${encodeURIComponent(ctx)}`);
  }

  return (
    <AppShell selectedModeId={modeId} onModeChange={setModeId}>
      <div className="mx-auto max-w-5xl p-6">
        <h1 className="mb-2 text-2xl font-semibold">{t("title")}</h1>
        <p className="mb-6 text-sm text-[var(--text-muted)]">{t("subtitle")}</p>

        <div className="mb-6 flex flex-wrap gap-3">
          <select
            value={source}
            onChange={(e) => setSource(e.target.value as (typeof SOURCES)[number])}
            className="rounded-lg border border-[var(--border)] bg-[var(--bg-panel)] px-3 py-2 text-sm"
          >
            {SOURCES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="min-w-[240px] flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg-panel)] px-3 py-2 text-sm"
            placeholder={t("searchPlaceholder")}
          />
          <button
            type="button"
            onClick={search}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            {t("search")}
          </button>
        </div>

        <div className="space-y-3">
          {items.map((item) => (
            <article key={item.url} className="rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] p-4">
              <div className="mb-1 flex items-center justify-between gap-2">
                <h2 className="font-medium">{item.title}</h2>
                <span className="text-xs text-[var(--text-muted)]">{item.source_type}</span>
              </div>
              <p className="mb-3 line-clamp-3 text-sm text-[var(--text-secondary)]">{item.excerpt}</p>
              <button
                type="button"
                onClick={() => openWithContext(item)}
                className="text-sm text-[var(--primary)] hover:underline"
              >
                {t("useAsContext")}
              </button>
            </article>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
