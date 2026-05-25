import type {
  GenerateResponse,
  PublicConfig,
  TemplateItem,
  TraceListItem,
  TraceResponse,
} from "./types";
import type { OutputLanguage } from "./output-language";
import type { AppLocale } from "@/i18n/routing";

const API_BASE =
  typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "/api"
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(
  path: string,
  init?: RequestInit,
  locale: AppLocale = "en",
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "Accept-Language": locale,
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function generateThread(
  context: string,
  mode: string,
  outputLanguage: OutputLanguage,
  locale: AppLocale,
  options?: {
    outputType?: string;
    thesisId?: string;
    voiceProfileId?: string;
    sourceUrls?: string[];
    quotedTweet?: string;
  },
) {
  return request<GenerateResponse>(
    "/generate",
    {
      method: "POST",
      body: JSON.stringify({
        context,
        mode,
        output_language: outputLanguage,
        output_type: options?.outputType ?? "thread",
        thesis_id: options?.thesisId,
        voice_profile_id: options?.voiceProfileId,
        source_urls: options?.sourceUrls ?? [],
        quoted_tweet: options?.quotedTweet ?? "",
      }),
    },
    locale,
  );
}

export function discoverContent(source: string, q: string) {
  return request<{ query: string; source: string; items: import("./platform-types").DiscoveryItem[]; cached: boolean }>(
    `/discover?source=${encodeURIComponent(source)}&q=${encodeURIComponent(q)}`,
  );
}

export function fetchVoices() {
  return request<{ voices: import("./platform-types").VoiceProfile[] }>("/voices");
}

export function createVoice(payload: { name: string; description: string; writing_samples: string[] }) {
  return request<import("./platform-types").VoiceProfile>("/voices", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchLaunchQueue() {
  return request<{ items: import("./platform-types").LaunchItem[] }>("/launch/queue");
}

export function runAutonomousResearch(payload: {
  topic: string;
  mode: string;
  output_type: string;
  output_language: string;
}) {
  return request<GenerateResponse>("/research/run", {
    method: "POST",
    body: JSON.stringify({ ...payload, auto_pick_thesis: true }),
  });
}

export function fetchTrace(traceId: string, locale: AppLocale) {
  return request<TraceResponse>(`/trace/${traceId}?locale=${locale}`, undefined, locale);
}

export function fetchTraces(limit = 50, offset = 0) {
  return request<{ traces: TraceListItem[]; total: number }>(
    `/traces?limit=${limit}&offset=${offset}`,
  );
}

export function fetchConfig(locale: AppLocale) {
  return request<PublicConfig>(`/config?locale=${locale}`, undefined, locale);
}

export function fetchTemplates() {
  return request<{ templates: TemplateItem[] }>("/templates");
}

export function createTemplate(payload: {
  name: string;
  description: string;
  context: string;
  default_mode: string;
}) {
  return request<TemplateItem>("/templates", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteTemplate(id: string) {
  return request<{ deleted: boolean; id: string }>(`/templates/${id}`, {
    method: "DELETE",
  });
}
