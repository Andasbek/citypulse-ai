"use client";

import { useState } from "react";
import ImpactCalculator from "@/components/ImpactCalculator";
import RecyclingMap from "@/components/RecyclingMap";

type SubTab = "calculator" | "recycling";

export default function EcoServicesSection() {
  const [tab, setTab] = useState<SubTab>("calculator");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold mb-1">Эко-сервисы</h1>
        <p className="text-sm text-text-secondary">Калькулятор экоследа и пункты переработки</p>
      </div>

      <div className="flex gap-1 bg-card border border-border rounded-lg p-1">
        {([
          { id: "calculator" as SubTab, label: "Калькулятор" },
          { id: "recycling" as SubTab, label: "Переработка" },
        ]).map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex-1 px-3 py-2 rounded-md text-sm transition-colors ${
              tab === t.id ? "bg-accent/10 text-accent font-medium" : "text-text-secondary hover:text-text"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "calculator" && <ImpactCalculator />}
      {tab === "recycling" && <RecyclingMap />}
    </div>
  );
}
