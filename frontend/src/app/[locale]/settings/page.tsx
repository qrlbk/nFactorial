"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { AppShell } from "@/components/AppShell";
import { OutputLanguagePicker } from "@/components/OutputLanguagePicker";
import { fetchConfig } from "@/lib/api";
import { DEFAULT_MODE_ID, MODE_IDS, type ModeId } from "@/lib/modes";
import {
  getOutputLanguage,
  setOutputLanguage,
  type OutputLanguage,
} from "@/lib/output-language";
import type { PublicConfig } from "@/lib/types";
import { translateThresholdKey, translateTracingSource } from "@/lib/i18n-display";
import type { AppLocale } from "@/i18n/routing";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tl = useTranslations("language");
  const tm = useTranslations("modes");
  const locale = useLocale() as AppLocale;
  const [selectedModeId, setSelectedModeId] = useState<ModeId>(DEFAULT_MODE_ID);
  const [outputLang, setOutputLang] = useState<OutputLanguage>("en");
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const [apiBase, setApiBase] = useState("/api");

  useEffect(() => {
    setOutputLang(getOutputLanguage());
    fetchConfig(locale).then(setConfig).catch(() => undefined);
    setApiBase(process.env.NEXT_PUBLIC_API_URL || "/api");
  }, [locale]);

  const outputLabels: Record<OutputLanguage, string> = {
    en: tl("en"),
    ru: tl("ru"),
    kk: tl("kk"),
  };

  return (
    <AppShell selectedModeId={selectedModeId} onModeChange={setSelectedModeId}>
      <section className="p-6">
        <h1 className="mb-6 text-xl font-semibold">{t("title")}</h1>

        <article className="panel mb-4 max-w-2xl p-4">
          <label className="mb-2 block text-xs font-semibold uppercase text-[var(--text-muted)]">
            {t("defaultMode")}
          </label>
          <select
            value={selectedModeId}
            onChange={(e) => setSelectedModeId(e.target.value as ModeId)}
            className="w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
          >
            {MODE_IDS.map((id) => (
              <option key={id} value={id}>
                {tm(`${id}.label`)}
              </option>
            ))}
          </select>
        </article>

        <article className="panel mb-4 max-w-2xl p-4">
          <OutputLanguagePicker
            value={outputLang}
            onChange={(lang) => {
              setOutputLang(lang);
              setOutputLanguage(lang);
            }}
            label={t("defaultOutputLanguage")}
            labels={outputLabels}
          />
        </article>

        <article className="panel mb-4 max-w-2xl p-4">
          <label className="mb-2 block text-xs font-semibold uppercase text-[var(--text-muted)]">
            {t("apiBase")}
          </label>
          <input
            value={apiBase}
            readOnly
            className="w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
          />
          <p className="mt-2 text-xs text-[var(--text-muted)]">{t("apiHint")}</p>
        </article>

        {config ? (
          <article className="panel max-w-2xl p-4">
            <h2 className="mb-3 text-sm font-medium">{t("thresholds")}</h2>
            <p className="mb-3 text-xs text-[var(--text-muted)]">
              {t("tracing")}: {translateTracingSource(config.tracing_source, t)}
            </p>
            <table className="w-full text-sm">
              <tbody>
                {Object.entries(config.thresholds).map(([key, value]) => (
                  <tr key={key} className="border-b border-[var(--border)]/50">
                    <td className="py-2 text-[var(--text-secondary)]">
                      {translateThresholdKey(key, t)}
                    </td>
                    <td className="py-2 font-mono">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
        ) : null}
      </section>
    </AppShell>
  );
}
