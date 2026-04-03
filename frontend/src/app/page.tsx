"use client";

import { useEffect, useState } from "react";
import { getOverview, getDashboard, type OverviewData, type DashboardData } from "@/lib/api";
import Sidebar from "@/components/Sidebar";
import OverviewSection from "@/components/OverviewSection";
import AnalyticsSection from "@/components/AnalyticsSection";
import AssistantSection from "@/components/AssistantSection";
import EcoServicesSection from "@/components/EcoServicesSection";

export type Section = "overview" | "analytics" | "assistant" | "eco";

export default function Home() {
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [section, setSection] = useState<Section>("overview");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getOverview(), getDashboard()])
      .then(([ov, db]) => { setOverview(ov); setDashboard(db); })
      .catch(() => setError("Не удалось загрузить данные. Убедитесь, что API запущен."));
  }, []);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="bg-card border border-border rounded-2xl p-10 text-center max-w-md">
          <div className="text-4xl mb-4">!</div>
          <p className="text-red font-medium mb-2">{error}</p>
          <code className="text-xs text-text-secondary bg-bg px-3 py-1.5 rounded-lg">
            cd backend && uvicorn api:app --reload
          </code>
        </div>
      </div>
    );
  }

  if (!overview || !dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
          <span className="text-sm text-text-secondary">Загрузка...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar section={section} onNavigate={setSection} overview={overview} />
      <main className="flex-1 ml-64 p-8 max-w-[1200px]">
        {section === "overview" && <OverviewSection data={overview} />}
        {section === "analytics" && <AnalyticsSection dashboard={dashboard} />}
        {section === "assistant" && <AssistantSection data={overview} />}
        {section === "eco" && <EcoServicesSection />}
      </main>
    </div>
  );
}
