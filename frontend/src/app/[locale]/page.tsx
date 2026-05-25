import { Suspense } from "react";
import { DashboardView } from "@/components/DashboardView";
import { LoadingFallback } from "@/components/LoadingFallback";

export default function HomePage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <DashboardView />
    </Suspense>
  );
}
