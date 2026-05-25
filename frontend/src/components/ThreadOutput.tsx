"use client";

import { useTranslations } from "next-intl";
import { Copy } from "lucide-react";

type Props = {
  index: number;
  text: string;
  maxChars?: number;
};

export function TweetCard({ index, text, maxChars = 280 }: Props) {
  return (
    <article className="rounded-lg border border-[var(--border)] bg-[#0f1218] p-4">
      <header className="mb-2 flex items-center justify-between">
        <span className="text-xs font-semibold text-[var(--primary)]">{index}</span>
        <span className="text-xs text-[var(--text-muted)]">
          {text.length}/{maxChars}
        </span>
      </header>
      <p className="text-sm leading-relaxed text-[var(--foreground)]">{text}</p>
    </article>
  );
}

type ThreadProps = {
  tweets: string[];
  refused?: boolean;
  refusalReason?: string | null;
  onCopyAll?: () => void;
};

export function ThreadOutput({ tweets, refused, refusalReason, onCopyAll }: ThreadProps) {
  const t = useTranslations("thread");

  return (
    <article className="panel flex h-full flex-col p-4">
      <header className="mb-4 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
          {t("title")}
        </span>
        {tweets.length > 0 && onCopyAll ? (
          <button
            type="button"
            onClick={onCopyAll}
            className="flex items-center gap-1 rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--text-secondary)] hover:text-white"
          >
            <Copy className="h-3.5 w-3.5" />
            {t("copyAll")}
          </button>
        ) : null}
      </header>

      <section className="flex-1 space-y-3 overflow-y-auto">
        {refused ? (
          <section className="rounded-lg border border-[var(--danger)]/40 bg-[var(--danger)]/10 p-4">
            <header className="mb-2 text-sm font-semibold text-[var(--danger)]">{t("refused")}</header>
            <p className="whitespace-pre-wrap text-sm text-[var(--danger)]/90">
              {refusalReason || t("refusedDefault")}
            </p>
          </section>
        ) : tweets.length === 0 ? (
          <p className="text-sm text-[var(--text-muted)]">{t("empty")}</p>
        ) : (
          tweets.map((tweet, i) => <TweetCard key={i} index={i + 1} text={tweet} />)
        )}
      </section>
    </article>
  );
}
