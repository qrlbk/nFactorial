"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { Trash2 } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { createTemplate, deleteTemplate, fetchTemplates } from "@/lib/api";
import { DEFAULT_MODE_ID, MODE_IDS, apiModeFromId, type ModeId } from "@/lib/modes";
import type { TemplateItem } from "@/lib/types";

export default function TemplatesPage() {
  const t = useTranslations("templates");
  const tm = useTranslations("modes");
  const [selectedModeId, setSelectedModeId] = useState<ModeId>(DEFAULT_MODE_ID);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [context, setContext] = useState("");

  const load = () => {
    fetchTemplates().then((r) => setTemplates(r.templates)).catch(() => undefined);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (context.length < 50 || !name.trim()) return;
    await createTemplate({
      name,
      description,
      context,
      default_mode: apiModeFromId(selectedModeId),
    });
    setName("");
    setDescription("");
    setContext("");
    load();
  };

  const handleDelete = async (id: string) => {
    await deleteTemplate(id);
    load();
  };

  return (
    <AppShell selectedModeId={selectedModeId} onModeChange={setSelectedModeId}>
      <section className="p-6">
        <h1 className="mb-6 text-xl font-semibold">{t("title")}</h1>

        <article className="panel mb-6 p-4">
          <h2 className="mb-3 text-sm font-medium">{t("create")}</h2>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("placeholders.name")}
            className="mb-2 w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
          />
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={t("placeholders.description")}
            className="mb-2 w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
          />
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder={t("placeholders.context")}
            className="mb-3 min-h-[120px] w-full rounded-lg border border-[var(--border)] bg-[#0f1218] p-3 text-sm"
          />
          <select
            value={selectedModeId}
            onChange={(e) => setSelectedModeId(e.target.value as ModeId)}
            className="mb-3 w-full rounded-lg border border-[var(--border)] bg-[#0f1218] px-3 py-2 text-sm"
          >
            {MODE_IDS.map((id) => (
              <option key={id} value={id}>
                {tm(`${id}.label`)}
              </option>
            ))}
          </select>
          <button type="button" onClick={() => void handleCreate()} className="btn-primary px-4 py-2 text-sm">
            {t("save")}
          </button>
        </article>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {templates.map((row) => (
            <article key={row.id} className="panel p-4">
              <header className="mb-2 flex items-start justify-between">
                <h3 className="font-medium">{row.name}</h3>
                <button
                  type="button"
                  onClick={() => void handleDelete(row.id)}
                  className="text-[var(--text-muted)] hover:text-[var(--danger)]"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </header>
              <p className="mb-2 text-xs text-[var(--text-muted)]">{row.description}</p>
              <p className="mb-3 line-clamp-3 text-sm text-[var(--text-secondary)]">{row.context}</p>
              <Link href="/" className="text-sm text-[var(--primary)] hover:underline">
                {t("loadTemplate")}
              </Link>
            </article>
          ))}
        </section>
      </section>
    </AppShell>
  );
}
