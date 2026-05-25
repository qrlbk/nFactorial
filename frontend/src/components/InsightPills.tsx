type Props = {
  insights: string[];
  emptyLabel: string;
};

export function InsightPills({ insights, emptyLabel }: Props) {
  if (insights.length === 0) {
    return <p className="text-xs text-[var(--text-muted)]">{emptyLabel}</p>;
  }

  return (
    <section className="flex flex-wrap gap-2">
      {insights.map((insight) => (
        <span
          key={insight}
          className="rounded-full border border-[var(--border)] bg-[#0f1218] px-3 py-1.5 text-xs text-[var(--text-secondary)]"
        >
          {insight}
        </span>
      ))}
    </section>
  );
}
