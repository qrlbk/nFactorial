"use client";

import { useTranslations } from "next-intl";
import type { VoiceProfile } from "@/lib/platform-types";

type Guidelines = VoiceProfile["guidelines"] & {
  sentence_rhythm?: string;
  opinion_strength?: string;
  vocabulary_notes?: string;
  taboo_phrases?: string[];
  reference_writers?: string[];
  sample_excerpt?: string;
};

type Props = {
  profile: VoiceProfile;
};

export function VoiceProfileCard({ profile }: Props) {
  const t = useTranslations("voice");
  const g = profile.guidelines as Guidelines;
  const excerpt = g.sample_excerpt?.trim();

  return (
    <article className="rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] p-4">
      <header className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h2 className="font-medium">{profile.name}</h2>
          <p className="font-mono text-xs text-[var(--text-muted)]">{profile.id}</p>
        </div>
        <button
          type="button"
          onClick={() => void navigator.clipboard.writeText(profile.id)}
          className="shrink-0 rounded border border-[var(--border)] px-2 py-1 text-xs text-[var(--text-secondary)] hover:text-white"
        >
          {t("copyId")}
        </button>
      </header>

      {excerpt ? (
        <section className="mb-4 rounded-lg border border-[var(--primary)]/30 bg-[var(--primary)]/5 p-4">
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-[var(--primary)]">
            {t("exampleText")}
          </p>
          <p className="text-sm leading-relaxed text-[var(--foreground)]">&ldquo;{excerpt}&rdquo;</p>
        </section>
      ) : null}

      <dl className="grid gap-2 text-xs text-[var(--text-secondary)]">
        {g.sentence_rhythm ? (
          <div>
            <dt className="font-medium text-[var(--text-muted)]">{t("rhythm")}</dt>
            <dd>{g.sentence_rhythm}</dd>
          </div>
        ) : null}
        {g.opinion_strength ? (
          <div>
            <dt className="font-medium text-[var(--text-muted)]">{t("opinion")}</dt>
            <dd>{g.opinion_strength}</dd>
          </div>
        ) : null}
        {g.vocabulary_notes ? (
          <div>
            <dt className="font-medium text-[var(--text-muted)]">{t("vocabulary")}</dt>
            <dd>{g.vocabulary_notes}</dd>
          </div>
        ) : null}
        {g.taboo_phrases && g.taboo_phrases.length > 0 ? (
          <div>
            <dt className="font-medium text-[var(--text-muted)]">{t("taboo")}</dt>
            <dd>{g.taboo_phrases.join(" · ")}</dd>
          </div>
        ) : null}
        {g.reference_writers && g.reference_writers.length > 0 ? (
          <div>
            <dt className="font-medium text-[var(--text-muted)]">{t("references")}</dt>
            <dd>{g.reference_writers.join(", ")}</dd>
          </div>
        ) : null}
      </dl>
    </article>
  );
}
