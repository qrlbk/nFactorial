"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Copy, Loader2, Plus, Share2 } from "lucide-react";
import { useRouter } from "@/i18n/navigation";
import { AppShell } from "@/components/AppShell";
import { CognitivePipelineStepper } from "@/components/CognitivePipelineStepper";
import { CognitiveJourneyPanel } from "@/components/CognitiveJourneyPanel";
import { OutputLanguagePicker } from "@/components/OutputLanguagePicker";
import { ThreadOutput } from "@/components/ThreadOutput";
import { ThreadStatsPanel } from "@/components/ThreadStatsPanel";
import { generateThread, fetchTrace } from "@/lib/api";
import { buildPipelineSteps, heuristicRunningStep } from "@/lib/pipeline-parser";
import { mapApiError } from "@/lib/i18n-display";
import {
  DEFAULT_MODE_ID,
  MODE_IDS,
  apiModeFromId,
  type ModeId,
} from "@/lib/modes";
import { setOutputLanguage, type OutputLanguage } from "@/lib/output-language";
import type { AppLocale } from "@/i18n/routing";
import type { OutputType } from "@/lib/platform-types";
import type { GenerateResponse, PipelineStepUI, TraceResponse } from "@/lib/types";

const DRAFT_KEY = "editorial-draft";

type Props = {
  initialTraceId?: string;
  initialContext?: string;
};

export function DashboardView({ initialTraceId, initialContext = "" }: Props) {
  const t = useTranslations();
  const tErrors = useTranslations("errors");
  const locale = useLocale() as AppLocale;
  const router = useRouter();
  const searchParams = useSearchParams();

  const [selectedModeId, setSelectedModeId] = useState<ModeId>(DEFAULT_MODE_ID);
  const [outputType, setOutputType] = useState<OutputType>("thread");
  const [quotedTweet, setQuotedTweet] = useState("");
  const [outputLang, setOutputLang] = useState<OutputLanguage>("en");
  const [context, setContext] = useState(initialContext);
  const [loading, setLoading] = useState(false);
  const [runningIndex, setRunningIndex] = useState(0);
  const [visibleCount, setVisibleCount] = useState(0);
  const [steps, setSteps] = useState<PipelineStepUI[]>([]);
  const [result, setResult] = useState<GenerateResponse | TraceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const replayRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    setOutputLang(locale);
    setOutputLanguage(locale);
    const ctx = searchParams.get("context");
    if (ctx) setContext(decodeURIComponent(ctx));
  }, [searchParams, locale]);

  const translateStep = useCallback(
    (node: string) => {
      if (MODE_IDS.includes(node as ModeId)) return node;
      try {
        return t(`pipeline.steps.${node}` as "pipeline.steps.context_qualification_gate");
      } catch {
        return node;
      }
    },
    [t],
  );

  const formatRetry = useCallback(
    (attempt: number) => t("pipeline.retryLabel", { attempt }),
    [t],
  );

  useEffect(() => {
    if (!initialTraceId) return;
    fetchTrace(initialTraceId, locale)
      .then((trace) => {
        setResult(trace);
        setContext(trace.input_preview || "");
        const built = buildPipelineSteps(
          trace.pipeline_timeline,
          trace.rejection_chain,
          translateStep,
          formatRetry,
        );
        setSteps(built);
        setVisibleCount(built.length);
      })
      .catch((e) => setError(mapApiError(e, tErrors)));
  }, [initialTraceId, locale, translateStep, formatRetry, tErrors]);

  const clearTimers = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    replayRef.current.forEach(clearTimeout);
    replayRef.current = [];
  }, []);

  const replaySteps = useCallback((built: PipelineStepUI[]) => {
    setVisibleCount(0);
    built.forEach((_, i) => {
      const timeout = setTimeout(() => setVisibleCount(i + 1), 400 + i * 500);
      replayRef.current.push(timeout);
    });
  }, []);

  const handleOutputLangChange = (lang: OutputLanguage) => {
    setOutputLang(lang);
    setOutputLanguage(lang);
  };

  const handleGenerate = async () => {
    if (context.trim().length < 50) {
      setError(t("errors.contextTooShort"));
      return;
    }
    clearTimers();
    setError(null);
    setLoading(true);
    setResult(null);
    setSteps([]);
    setVisibleCount(0);
    setRunningIndex(0);

    const start = Date.now();
    timerRef.current = setInterval(() => {
      setRunningIndex(heuristicRunningStep(Date.now() - start));
    }, 600);

    try {
      const res = await generateThread(
        context,
        apiModeFromId(selectedModeId),
        outputLang,
        locale,
        { outputType, quotedTweet: outputType === "quote_retweet" ? quotedTweet : undefined },
      );
      clearTimers();
      setLoading(false);
      setResult(res);
      const built = buildPipelineSteps(
        res.pipeline_timeline,
        res.rejection_history,
        translateStep,
        formatRetry,
      );
      setSteps(built);
      replaySteps(built);
    } catch (e) {
      clearTimers();
      setLoading(false);
      setError(mapApiError(e, tErrors));
    }
  };

  const tweets = result?.final_thread || (result as TraceResponse)?.output_thread || [];
  const refused = result?.refused ?? false;
  const traceId = result?.trace_id;
  const rejections =
    result?.rejection_history || (result as TraceResponse)?.rejection_chain || [];
  const timeline = result?.pipeline_timeline || [];
  const insights = result?.key_insights || [];
  const stats = result?.thread_stats || null;
  const hooks = result?.hook_variants || [];
  const factCheck = result?.fact_check_report || {};

  const outputLabels: Record<OutputLanguage, string> = {
    en: t("language.en"),
    ru: t("language.ru"),
    kk: t("language.kk"),
  };

  const copyTrace = () => {
    if (!traceId) return;
    void navigator.clipboard.writeText(`${window.location.origin}/${locale}/traces/${traceId}`);
  };

  const copyTweets = () => {
    void navigator.clipboard.writeText(tweets.join("\n\n"));
  };

  const saveDraft = () => {
    localStorage.setItem(
      DRAFT_KEY,
      JSON.stringify({ context, modeId: selectedModeId, outputLang }),
    );
  };

  const reset = () => {
    setResult(null);
    setSteps([]);
    setVisibleCount(0);
    setError(null);
    router.push("/");
  };

  return (
    <AppShell selectedModeId={selectedModeId} onModeChange={setSelectedModeId}>
      <section className="p-6">
        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <section>
            <h1 className="text-xl font-semibold">{t("dashboard.title")}</h1>
            {traceId ? (
              <section className="mt-2 flex items-center gap-2">
                <span className="rounded-full border border-[var(--border)] bg-[var(--bg-panel)] px-3 py-1 font-mono text-xs text-[var(--text-secondary)]">
                  {t("dashboard.traceId")}: {traceId.slice(0, 8)}…
                </span>
                <button
                  type="button"
                  onClick={() => void navigator.clipboard.writeText(traceId)}
                  className="text-[var(--text-muted)] hover:text-white"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </section>
            ) : null}
          </section>
          <section className="flex gap-2">
            <button
              type="button"
              onClick={copyTrace}
              disabled={!traceId}
              className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-white disabled:opacity-40"
            >
              <Share2 className="h-4 w-4" />
              {t("dashboard.shareTrace")}
            </button>
            <button
              type="button"
              onClick={saveDraft}
              className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-white"
            >
              {t("dashboard.saveDraft")}
            </button>
            <button type="button" onClick={reset} className="btn-primary flex items-center gap-2 px-4 py-2 text-sm">
              <Plus className="h-4 w-4" />
              {t("dashboard.generateNew")}
            </button>
          </section>
        </header>

        {error ? (
          <section className="mb-4 rounded-lg border border-[var(--danger)]/40 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
            {error}
          </section>
        ) : null}

        <section className="grid min-h-[520px] grid-cols-1 gap-4 xl:grid-cols-3">
          <article className="panel flex flex-col p-4">
            <header className="mb-2 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
              {t("dashboard.pasteContext")}
            </header>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder={t("dashboard.contextPlaceholder")}
              className="min-h-[240px] flex-1 resize-none rounded-lg border border-[var(--border)] bg-[#0f1218] p-3 text-sm text-[var(--foreground)] outline-none focus:border-[var(--primary)]"
            />
            <footer className="mt-2 flex items-center justify-between text-xs text-[var(--text-muted)]">
              <span>{t("dashboard.characters", { count: context.length })}</span>
              <button type="button" onClick={() => setContext("")} className="hover:text-white">
                {t("dashboard.clear")}
              </button>
            </footer>
            <p className="mt-2 text-xs leading-relaxed text-[var(--text-muted)]">
              {t("dashboard.contextLanguageHint")}
            </p>
            <section className="mt-4 space-y-4">
              <section>
                <header className="mb-2 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                  {t("dashboard.selectMode")}
                </header>
                <select
                  value={selectedModeId}
                  onChange={(e) => setSelectedModeId(e.target.value as ModeId)}
                  className="w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
                >
                  {MODE_IDS.map((id) => (
                    <option key={id} value={id}>
                      {t(`modes.${id}.label`)}
                    </option>
                  ))}
                </select>
              </section>
              <section>
                <header className="mb-2 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                  Format
                </header>
                <select
                  value={outputType}
                  onChange={(e) => setOutputType(e.target.value as OutputType)}
                  className="w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
                >
                  {(["thread", "quote_retweet", "essay"] as OutputType[]).map((fmt) => (
                    <option key={fmt} value={fmt}>{t(`formats.${fmt}`)}</option>
                  ))}
                </select>
              </section>
              {outputType === "quote_retweet" ? (
                <section>
                  <header className="mb-2 text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                    Quoted tweet
                  </header>
                  <textarea
                    value={quotedTweet}
                    onChange={(e) => setQuotedTweet(e.target.value)}
                    rows={3}
                    className="w-full rounded-lg border border-[var(--border)] bg-[#0f1218] p-3 text-sm"
                  />
                </section>
              ) : null}
              <OutputLanguagePicker
                value={outputLang}
                onChange={handleOutputLangChange}
                label={t("dashboard.outputLanguage")}
                labels={outputLabels}
              />
            </section>
            <button
              type="button"
              onClick={() => void handleGenerate()}
              disabled={loading}
              className="btn-primary mt-4 flex w-full items-center justify-center gap-2 py-3 text-sm"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              {t("dashboard.generateThread")}
            </button>
          </article>

          <CognitivePipelineStepper
            steps={steps}
            visibleCount={visibleCount}
            loading={loading}
            runningIndex={runningIndex}
          />

          <section className="flex flex-col">
            <ThreadOutput
              tweets={tweets}
              refused={refused}
              refusalReason={result?.refusal_reason}
              onCopyAll={copyTweets}
            />
            <ThreadStatsPanel stats={stats} />
            {hooks.length > 0 ? (
              <section className="panel mt-4 p-4">
                <header className="mb-2 text-xs font-semibold uppercase text-[var(--text-muted)]">Hook variants</header>
                <ul className="space-y-2 text-sm">{hooks.map((h) => <li key={h}>{h}</li>)}</ul>
              </section>
            ) : null}
            {factCheck && Object.keys(factCheck).length > 0 ? (
              <section className="panel mt-4 p-4">
                <header className="mb-2 text-xs font-semibold uppercase text-[var(--text-muted)]">Fact check</header>
                <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(factCheck, null, 2)}</pre>
              </section>
            ) : null}
          </section>
        </section>

        <CognitiveJourneyPanel rejections={rejections} timeline={timeline} insights={insights} />
      </section>
    </AppShell>
  );
}
