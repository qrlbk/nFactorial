"use client";

import type { OutputLanguage } from "@/lib/output-language";

type Props = {
  value: OutputLanguage;
  onChange: (lang: OutputLanguage) => void;
  label: string;
  labels: Record<OutputLanguage, string>;
};

export function OutputLanguagePicker({ value, onChange, label, labels }: Props) {
  return (
    <section>
      <label className="mb-2 block text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as OutputLanguage)}
        className="w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
      >
        {(["en", "ru", "kk"] as OutputLanguage[]).map((code) => (
          <option key={code} value={code}>
            {labels[code]}
          </option>
        ))}
      </select>
    </section>
  );
}
