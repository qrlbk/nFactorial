export type OutputType = "thread" | "quote_retweet" | "essay" | "article";

export type DiscoveryItem = {
  title: string;
  url: string;
  excerpt: string;
  source_type: string;
  published_at: string | null;
  relevance_score: number;
  author?: string | null;
};

export type VoiceProfile = {
  id: string;
  name: string;
  description: string;
  guidelines: Record<string, unknown>;
  created_at: string;
};

export type LaunchItem = {
  id: string;
  output_type: string;
  content: string[] | string;
  mode: string;
  trace_id: string | null;
  status: string;
  scheduled_at: string | null;
  created_at: string;
};

export type ThesisCandidate = {
  id: string;
  hook: string;
  defended_claim: string;
  attacked_consensus: string;
  intellectual_risk_level: number;
  thesis_confidence: number;
};
