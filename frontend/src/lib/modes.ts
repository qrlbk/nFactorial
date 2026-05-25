export const MODE_IDS = ["contrarian-vc", "paul-graham", "research-analyst"] as const;

export type ModeId = (typeof MODE_IDS)[number];

export const MODE_TO_API: Record<ModeId, string> = {
  "contrarian-vc": "Contrarian VC",
  "paul-graham": "Paul Graham",
  "research-analyst": "Research Analyst",
};

export const DEFAULT_MODE_ID: ModeId = "contrarian-vc";

export function apiModeFromId(modeId: string): string {
  return MODE_TO_API[modeId as ModeId] ?? MODE_TO_API[DEFAULT_MODE_ID];
}
