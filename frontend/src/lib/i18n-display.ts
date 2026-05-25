export type DisplayTranslator = (
  key: string,
  values?: Record<string, string | number>,
) => string;

const PIPELINE_STATUSES = [
  "pending",
  "running",
  "done",
  "qualified",
  "borderline",
  "passed",
  "approved",
  "rejected",
  "refused",
  "fail_closed",
  "retry",
] as const;

export function translatePipelineStatus(status: string, t: DisplayTranslator): string {
  const normalized = status.toLowerCase().replace(/\s+/g, "_");
  if (PIPELINE_STATUSES.includes(normalized as (typeof PIPELINE_STATUSES)[number])) {
    return t(`status.${normalized}`);
  }
  return status;
}

export function translateTraceStatus(status: string, t: DisplayTranslator): string {
  const normalized = status.toLowerCase();
  if (normalized === "success") return t("statusSuccess");
  if (normalized === "refused") return t("statusRefused");
  return status;
}

const THRESHOLD_KEYS = [
  "min_thesis_confidence",
  "min_input_worthiness_score",
  "min_specificity_score",
  "min_anchor_preservation_ratio",
  "max_critic_retries",
  "thread_min",
  "thread_max",
  "tweet_max_chars",
] as const;

export function translateThresholdKey(key: string, t: DisplayTranslator): string {
  if (THRESHOLD_KEYS.includes(key as (typeof THRESHOLD_KEYS)[number])) {
    return t(`thresholdKeys.${key}`);
  }
  return key.replace(/_/g, " ");
}

export function translateTracingSource(source: string, t: DisplayTranslator): string {
  if (source === "local") return t("tracingLocal");
  if (source === "langfuse") return t("tracingLangfuse");
  return source;
}

export function formatSeconds(durationMs: number, t: DisplayTranslator): string {
  const seconds = (durationMs / 1000).toFixed(1);
  return t("seconds", { n: seconds });
}

export function mapApiError(error: unknown, t: DisplayTranslator): string {
  if (!(error instanceof Error)) {
    return t("generateFailed");
  }

  const msg = error.message.toLowerCase();

  if (msg.includes("failed to fetch") || msg.includes("networkerror") || msg.includes("load failed")) {
    return t("networkError");
  }

  if (msg.includes("50") && (msg.includes("context") || msg.includes("character"))) {
    return t("contextTooShort");
  }

  try {
    const parsed = JSON.parse(error.message) as { detail?: unknown };
    const detail = String(parsed.detail ?? "").toLowerCase();
    if (detail.includes("50") && detail.includes("context")) {
      return t("contextTooShort");
    }
  } catch {
    // not JSON
  }

  if (error.message.includes("404") || msg.includes("not found")) {
    return t("traceNotFound");
  }

  return t("generateFailed");
}
