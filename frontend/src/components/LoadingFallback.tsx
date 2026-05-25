"use client";

import { useTranslations } from "next-intl";

export function LoadingFallback() {
  const t = useTranslations("errors");
  return <p className="p-6 text-sm text-[var(--text-muted)]">{t("loading")}</p>;
}
