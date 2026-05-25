import { use } from "react";
import { DashboardView } from "@/components/DashboardView";

type Props = {
  params: Promise<{ id: string }>;
};

export default function TraceDetailPage({ params }: Props) {
  const { id } = use(params);
  return <DashboardView initialTraceId={id} />;
}
