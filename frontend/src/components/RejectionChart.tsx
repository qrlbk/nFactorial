"use client";

import type { RejectionEvent } from "@/lib/types";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Props = {
  rejections: RejectionEvent[];
  emptyLabel: string;
  attemptLabel: (n: number) => string;
};

export function RejectionChart({ rejections, emptyLabel, attemptLabel }: Props) {
  const data = rejections.map((r, i) => ({
    name: attemptLabel(i + 1),
    count: 1,
    node: r.node.replace(/_/g, " ").slice(0, 12),
  }));

  if (data.length === 0) {
    return (
      <section className="flex h-32 items-center justify-center text-xs text-[var(--text-muted)]">
        {emptyLabel}
      </section>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={120}>
      <BarChart data={data}>
        <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis hide domain={[0, 1]} />
        <Tooltip
          contentStyle={{
            background: "#12151c",
            border: "1px solid #1e2430",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Bar dataKey="count" fill="#ef4444" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
