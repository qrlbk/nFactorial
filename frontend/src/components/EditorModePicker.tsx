"use client";

import { useTranslations } from "next-intl";
import { MODE_IDS, type ModeId } from "@/lib/modes";

type Props = {
  selectedModeId: ModeId;
  onModeChange: (modeId: ModeId) => void;
  title: string;
};

export function EditorModePicker({ selectedModeId, onModeChange, title }: Props) {
  const t = useTranslations("modes");

  return (
    <div>
      <div className="mb-3 px-2 text-[10px] font-semibold uppercase tracking-widest text-[var(--text-muted)]">
        {title}
      </div>
      <div className="space-y-2">
        {MODE_IDS.map((id) => {
          const active = selectedModeId === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => onModeChange(id)}
              className={`w-full rounded-lg border px-3 py-2 text-left transition ${
                active
                  ? "border-[var(--primary)] bg-[var(--primary)]/10"
                  : "border-[var(--border)] bg-[var(--bg-panel)] hover:border-[var(--primary)]/40"
              }`}
            >
              <div className="text-sm font-medium">{t(`${id}.label`)}</div>
              <div className="text-xs text-[var(--text-muted)]">{t(`${id}.description`)}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
