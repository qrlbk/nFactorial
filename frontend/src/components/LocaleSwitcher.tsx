"use client";

import { useLocale } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";

const LOCALES: AppLocale[] = ["en", "ru", "kk"];

type Props = {
  labels: Record<AppLocale, string>;
  uiLabel: string;
};

export function LocaleSwitcher({ labels, uiLabel }: Props) {
  const locale = useLocale() as AppLocale;
  const router = useRouter();
  const pathname = usePathname();

  return (
    <div className="mb-4 px-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-[var(--text-muted)]">
        {uiLabel}
      </div>
      <div className="flex gap-1">
        {LOCALES.map((code) => (
          <button
            key={code}
            type="button"
            onClick={() => router.replace(pathname, { locale: code })}
            className={`flex-1 rounded-lg border px-2 py-1.5 text-xs transition ${
              locale === code
                ? "border-[var(--primary)] bg-[var(--primary)]/15 text-[var(--primary)]"
                : "border-[var(--border)] text-[var(--text-muted)] hover:text-white"
            }`}
          >
            {labels[code]}
          </button>
        ))}
      </div>
    </div>
  );
}
