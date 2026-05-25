import type { ThesisCandidate } from "./platform-types";

export type PipelineStepRecord = {
  node: string;
  status: string;
  duration_ms: number;
  detail: string;
};

export type ThreadStats = {
  tweet_count: number;
  total_characters: number;
  signal_density: number;
  signal_density_label: string;
  mechanistic_layers: number;
  mechanistic_layers_target: number;
  epistemic_preserved: boolean;
  open_question_preserved: boolean;
  uncertainty_signals_kept: boolean;
  no_false_closure: boolean;
};

export type RejectionEvent = {
  node: string;
  timestamp: string;
  reason: string;
  failed_metrics: Record<string, unknown>;
  rejected_excerpt: string;
};

export type GenerateResponse = {
  final_thread: string[] | null;
  trace_id: string | null;
  rejection_history: RejectionEvent[];
  refused: boolean;
  refusal_reason: string | null;
  pipeline_log: string[];
  pipeline_timeline: PipelineStepRecord[];
  thread_stats: ThreadStats | null;
  key_insights: string[];
  total_retries: number;
  input_worthiness_score: number;
  output_type?: string;
  thesis_candidates?: ThesisCandidate[];
  final_output?: Record<string, unknown>;
  hook_variants?: string[];
  fact_check_report?: Record<string, unknown>;
};

export type TraceResponse = GenerateResponse & {
  trace_id: string;
  rejection_chain: RejectionEvent[];
  cognition_stages: Record<string, unknown>;
  langfuse_url: string | null;
  output_thread: string[] | null;
  input_preview: string;
  mode: string;
  status: string;
};

export type TraceListItem = {
  trace_id: string;
  created_at: string;
  mode: string;
  status: string;
  preview: string;
  tweet_count: number;
  total_retries: number;
};

export type EditorMode = {
  id: string;
  label: string;
  description: string;
};

export type TemplateItem = {
  id: string;
  name: string;
  description: string;
  context: string;
  default_mode: string;
  created_at: string;
};

export type PublicConfig = {
  service_name: string;
  tracing_source: string;
  editor_modes: EditorMode[];
  thresholds: Record<string, number>;
};

export type PipelineStepUI = {
  id: string;
  label: string;
  status: "pending" | "running" | "done" | "qualified" | "borderline" | "passed" | "approved" | "rejected" | "refused" | "fail_closed";
  durationMs?: number;
  detail?: string;
  reason?: string;
  retryLabel?: string;
};
