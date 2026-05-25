"use client";

import { Link, usePathname } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
import { Brain, Compass, FileText, History, Megaphone, Mic, Settings, Sparkles } from "lucide-react";
import { ApiStatusBanner } from "./ApiStatusBanner";
import { LocaleSwitcher } from "./LocaleSwitcher";
import { EditorModePicker } from "./EditorModePicker";
import type { ModeId } from "@/lib/modes";
import type { AppLocale } from "@/i18n/routing";

type Props = {
  children: React.ReactNode;
  selectedModeId: ModeId;
  onModeChange: (modeId: ModeId) => void;
};

export function AppShell({ children, selectedModeId, onModeChange }: Props) {
  const t = useTranslations();
  const pathname = usePathname();

  const nav = [
    { href: "/", label: t("nav.newThread"), icon: Sparkles },
    { href: "/discover", label: t("nav.discover"), icon: Compass },
    { href: "/voice", label: t("nav.voice"), icon: Mic },
    { href: "/launch", label: t("nav.launch"), icon: Megaphone },
    { href: "/history", label: t("nav.history"), icon: History },
    { href: "/templates", label: t("nav.templates"), icon: FileText },
    { href: "/settings", label: t("nav.settings"), icon: Settings },
  ] as const;

  const localeLabels: Record<AppLocale, string> = {
    en: t("language.en"),
    ru: t("language.ru"),
    kk: t("language.kk"),
  };

  return (
    <div className="flex min-h-screen">
      <aside className="fixed left-0 top-0 flex h-screen w-60 flex-col border-r border-[var(--border)] bg-[#0a0d12] px-4 py-5">
        <div className="mb-6 flex items-center gap-2 px-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--primary)]/20">
            <Brain className="h-5 w-5 text-[var(--primary)]" />
          </div>
          <div>
            <div className="text-sm font-semibold">{t("brand.title")}</div>
            <div className="text-[10px] uppercase tracking-widest text-[var(--text-muted)]">
              {t("brand.subtitle")}
            </div>
          </div>
        </div>

        <nav className="space-y-1">
          {nav.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.label}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
                  active
                    ? "bg-[var(--primary)]/15 text-[var(--primary)]"
                    : "text-[var(--text-secondary)] hover:bg-[var(--bg-panel)] hover:text-white"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <LocaleSwitcher labels={localeLabels} uiLabel={t("language.uiLabel")} />

        <div className="mt-4 flex-1">
          <EditorModePicker
            selectedModeId={selectedModeId}
            onModeChange={onModeChange}
            title={t("modes.title")}
          />
        </div>

        <div className="mt-auto flex items-center gap-3 rounded-lg border border-[var(--border)] bg-[var(--bg-panel)] p-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--primary)] text-sm font-bold">
            AS
          </div>
          <div>
            <div className="text-sm font-medium">{t("profile.name")}</div>
            <div className="text-xs text-[var(--primary)]">{t("profile.plan")}</div>
          </div>
        </div>
      </aside>

      <main className="ml-60 min-h-screen flex-1">
        <ApiStatusBanner />
        {children}
      </main>
    </div>
  );
}
