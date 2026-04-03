"use client";

import type { Section } from "@/app/page";
import type { OverviewData } from "@/lib/api";

const nav: { id: Section; label: string; icon: string }[] = [
  { id: "overview", label: "Обзор", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1" },
  { id: "analytics", label: "Аналитика", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { id: "assistant", label: "Помощник", icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" },
  { id: "eco", label: "Эко-сервисы", icon: "M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
];

const statusLabel = { normal: "Норма", warning: "Внимание", critical: "Критично" };
const statusColor = { normal: "bg-green", warning: "bg-orange", critical: "bg-red" };

export default function Sidebar({
  section,
  onNavigate,
  overview,
}: {
  section: Section;
  onNavigate: (s: Section) => void;
  overview: OverviewData;
}) {
  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-card border-r border-border flex flex-col z-50">
      {/* Logo */}
      <div className="p-5 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent/20 text-accent flex items-center justify-center text-sm font-bold">
            CP
          </div>
          <div>
            <div className="text-sm font-semibold">CityPulse AI</div>
            <div className="text-[11px] text-text-secondary">Алматы</div>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2 mb-2">
          <span className={`w-2 h-2 rounded-full ${statusColor[overview.city_status]} animate-pulse`} />
          <span className="text-xs font-medium">{statusLabel[overview.city_status]}</span>
        </div>
        <div className="flex gap-3 text-[11px] text-text-secondary">
          <span>{overview.total_issues} проблем</span>
          {overview.top_kpis.critical_count > 0 && (
            <span className="text-red">{overview.top_kpis.critical_count} крит.</span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3">
        {nav.map((item) => {
          const active = section === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm mb-1 transition-colors ${
                active
                  ? "bg-accent/10 text-accent font-medium"
                  : "text-text-secondary hover:text-text hover:bg-card-hover"
              }`}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d={item.icon} />
              </svg>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="text-[10px] text-text-secondary text-center">
          {overview.ai_powered ? "AI подключен" : "Rule-based режим"}
        </div>
      </div>
    </aside>
  );
}
