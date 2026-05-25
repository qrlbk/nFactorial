"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AppShell } from "@/components/AppShell";
import { VoiceProfileCard } from "@/components/VoiceProfileCard";
import { createVoice, fetchVoices } from "@/lib/api";
import { VOICE_SAMPLE_EXAMPLE } from "@/lib/voice-example";
import type { VoiceProfile } from "@/lib/platform-types";
import { DEFAULT_MODE_ID, type ModeId } from "@/lib/modes";

export default function VoicePage() {
  const t = useTranslations("voice");
  const [modeId, setModeId] = useState<ModeId>(DEFAULT_MODE_ID);
  const [voices, setVoices] = useState<VoiceProfile[]>([]);
  const [name, setName] = useState("");
  const [samples, setSamples] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVoices().then((r) => setVoices(r.voices)).catch(() => setVoices([]));
  }, []);

  async function handleCreate() {
    setLoading(true);
    setError(null);
    try {
      const sampleList = samples.split("\n---\n").map((s) => s.trim()).filter(Boolean);
      await createVoice({
        name,
        description: "",
        writing_samples: sampleList.length ? sampleList : [samples],
      });
      const r = await fetchVoices();
      setVoices(r.voices);
      setName("");
      setSamples("");
    } catch (e) {
      setError(e instanceof Error ? e.message : t("createError"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell selectedModeId={modeId} onModeChange={setModeId}>
      <div className="mx-auto max-w-3xl p-6">
        <h1 className="mb-2 text-2xl font-semibold">{t("title")}</h1>
        <p className="mb-6 text-sm text-[var(--text-muted)]">{t("subtitle")}</p>

        <div className="mb-8 space-y-3 rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] p-4">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("namePlaceholder")}
            className="w-full rounded-lg border border-[var(--border)] bg-[#0a0d12] px-3 py-2 text-sm"
          />
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs text-[var(--text-muted)]">{t("samplesLabel")}</span>
            <button
              type="button"
              onClick={() => setSamples(VOICE_SAMPLE_EXAMPLE)}
              className="text-xs text-[var(--primary)] hover:underline"
            >
              {t("loadExample")}
            </button>
          </div>
          <textarea
            value={samples}
            onChange={(e) => setSamples(e.target.value)}
            placeholder={t("samplesPlaceholder")}
            rows={10}
            className="w-full rounded-lg border border-[var(--border)] bg-[#0a0d12] px-3 py-2 text-sm leading-relaxed"
          />
          <p className="text-xs text-[var(--text-muted)]">
            {t("charCount", { count: samples.length })}
          </p>
          {error ? (
            <p className="text-sm text-[var(--danger)]">{error}</p>
          ) : null}
          <button
            type="button"
            onClick={() => void handleCreate()}
            disabled={loading || !name.trim() || samples.length < 50}
            className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {loading ? t("creating") : t("create")}
          </button>
        </div>

        {voices.length > 0 ? (
          <section>
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
              {t("savedProfiles")}
            </h2>
            <div className="space-y-3">
              {voices.map((v) => (
                <VoiceProfileCard key={v.id} profile={v} />
              ))}
            </div>
          </section>
        ) : (
          <p className="text-sm text-[var(--text-muted)]">{t("emptyList")}</p>
        )}
      </div>
    </AppShell>
  );
}
