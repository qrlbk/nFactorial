"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AlertTriangle } from "lucide-react";

const API_BASE =
  typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "/api"
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ApiStatusBanner() {
  const t = useTranslations("deploy");
  const [unreachable, setUnreachable] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
        if (!res.ok) throw new Error(String(res.status));
        if (!cancelled) setUnreachable(false);
      } catch {
        if (!cancelled) setUnreachable(true);
      }
    }

    void check();
    const id = window.setInterval(check, 60_000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  if (!unreachable) return null;

  return (
    <div
      role="alert"
      className="flex items-start gap-3 border-b border-amber-500/30 bg-amber-500/10 px-6 py-3 text-sm text-amber-100"
    >
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
      <div>
        <p className="font-medium">{t("apiUnreachable")}</p>
        <p className="mt-1 text-xs text-amber-200/80">{t("apiUnreachableHint")}</p>
      </div>
    </div>
  );
}
