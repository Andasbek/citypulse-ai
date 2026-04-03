"use client";

import { useState } from "react";
import type { DashboardData } from "@/lib/api";
import TransportTab from "@/components/TransportTab";
import EcologyTab from "@/components/EcologyTab";
import CombinedTab from "@/components/CombinedTab";

type SubTab = "transport" | "ecology" | "combined";

const tabs: { id: SubTab; label: string }[] = [
  { id: "transport", label: "Транспорт" },
  { id: "ecology", label: "Экология" },
  { id: "combined", label: "Комбинированный" },
];

export default function AnalyticsSection({ dashboard }: { dashboard: DashboardData }) {
  const [tab, setTab] = useState<SubTab>("transport");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold mb-1">Аналитика</h1>
        <p className="text-sm text-text-secondary">Детальные графики и проблемы</p>
      </div>

      {/* Sub-tabs */}
      <div className="flex gap-1 bg-card border border-border rounded-lg p-1">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex-1 px-3 py-2 rounded-md text-sm transition-colors ${
              tab === t.id
                ? "bg-accent/10 text-accent font-medium"
                : "text-text-secondary hover:text-text"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "transport" && <TransportTab issues={dashboard.issues} />}
      {tab === "ecology" && <EcologyTab issues={dashboard.issues} />}
      {tab === "combined" && <CombinedTab combinedIssues={dashboard.combined_issues} />}
    </div>
  );
}
