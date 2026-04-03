"use client";

import { useState } from "react";
import type { OverviewData, DistrictData } from "@/lib/api";
import DistrictMap from "@/components/DistrictMap";

const statusColor = { normal: "text-green", warning: "text-orange", critical: "text-red" };
const statusBg = { normal: "bg-green-bg", warning: "bg-orange-bg", critical: "bg-red-bg" };

export default function OverviewSection({ data }: { data: OverviewData }) {
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictData | null>(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold mb-1">Обзор города</h1>
        <p className="text-sm text-text-secondary">Текущее состояние Алматы</p>
      </div>

      {/* 4 KPI */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Загруженность"
          value={`${data.top_kpis.avg_congestion}%`}
          sub="среднее по городу"
          status={data.top_kpis.avg_congestion >= 60 ? "critical" : data.top_kpis.avg_congestion >= 40 ? "warning" : "normal"}
        />
        <KpiCard
          label="Качество воздуха"
          value={String(data.top_kpis.avg_aqi)}
          sub="AQI"
          status={data.top_kpis.avg_aqi > 100 ? "critical" : data.top_kpis.avg_aqi > 50 ? "warning" : "normal"}
        />
        <KpiCard
          label="Критические"
          value={String(data.top_kpis.critical_count)}
          sub="проблем"
          status={data.top_kpis.critical_count > 0 ? "critical" : "normal"}
        />
        <KpiCard
          label="Risk Score"
          value={String(data.top_kpis.risk_score)}
          sub="из 100"
          status={data.top_kpis.risk_score >= 60 ? "critical" : data.top_kpis.risk_score >= 35 ? "warning" : "normal"}
        />
      </div>

      {/* Map + District card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="text-sm font-medium mb-4">Карта районов</h2>
            <DistrictMap
              districts={data.districts}
              selected={selectedDistrict}
              onSelect={setSelectedDistrict}
            />
          </div>
        </div>

        <div className="space-y-4">
          {/* District detail card */}
          {selectedDistrict ? (
            <div className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium">{selectedDistrict.district}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusBg[selectedDistrict.status]} ${statusColor[selectedDistrict.status]}`}>
                  {selectedDistrict.status === "critical" ? "Критично" : selectedDistrict.status === "warning" ? "Внимание" : "Норма"}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <Stat label="Загруженность" value={`${selectedDistrict.avg_congestion}%`} />
                <Stat label="AQI" value={String(selectedDistrict.avg_aqi)} />
                <Stat label="Скорость" value={`${selectedDistrict.avg_speed} км/ч`} />
                <Stat label="Risk" value={String(selectedDistrict.risk_score)} />
              </div>
              <div className="text-xs text-text-secondary mb-2">
                Проблем: {selectedDistrict.issue_count} (крит. {selectedDistrict.critical_count})
              </div>
              <p className="text-xs text-text-secondary leading-relaxed border-t border-border pt-3">
                {selectedDistrict.recommendation}
              </p>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-5 flex items-center justify-center h-[200px]">
              <p className="text-xs text-text-secondary">Кликните на район на карте</p>
            </div>
          )}

          {/* Problem districts */}
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
              Проблемные районы
            </h3>
            <div className="space-y-2">
              {data.top_problem_districts.map((d) => (
                <button
                  key={d.district}
                  onClick={() => setSelectedDistrict(d)}
                  className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-card-hover transition-colors text-left"
                >
                  <div className="flex items-center gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${d.status === "critical" ? "bg-red" : "bg-orange"}`} />
                    <span className="text-sm">{d.district}</span>
                  </div>
                  <span className={`text-xs font-medium ${statusColor[d.status]}`}>
                    {d.risk_score}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* AI Summary */}
      <div className="bg-card border border-border rounded-xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded bg-accent/20 flex items-center justify-center">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-accent">
              <path d="M12 2a5 5 0 015 5c0 2-1 3-2 4l-1 1v2h-4v-2l-1-1c-1-1-2-2-2-4a5 5 0 015-5z" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2 className="text-sm font-medium">AI-анализ</h2>
          <span className="text-[10px] text-text-secondary bg-bg px-2 py-0.5 rounded">
            {data.ai_powered ? "GPT" : "Rule-based"}
          </span>
        </div>
        <p className="text-sm text-text-secondary leading-relaxed">{data.summary}</p>
      </div>

      {/* Critical alerts + Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Alerts */}
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
            Критические проблемы
          </h3>
          {data.critical_alerts.length > 0 ? (
            <div className="space-y-2">
              {data.critical_alerts.map((alert, i) => (
                <div key={i} className="flex items-start gap-2 p-2.5 bg-red-bg rounded-lg">
                  <span className="w-1.5 h-1.5 rounded-full bg-red mt-1.5 flex-shrink-0" />
                  <div>
                    <div className="text-xs font-medium">{alert.district}</div>
                    <div className="text-[11px] text-text-secondary">{alert.description}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-text-secondary">Критических проблем нет</p>
          )}
        </div>

        {/* Recommendations */}
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
            Рекомендации
          </h3>
          <div className="space-y-2">
            {data.recommendations.map((rec, i) => {
              const color = rec.priority === "high" ? "bg-red" : rec.priority === "medium" ? "bg-orange" : "bg-green";
              return (
                <div key={i} className="flex items-start gap-2 p-2.5 bg-bg rounded-lg">
                  <span className={`w-1.5 h-1.5 rounded-full ${color} mt-1.5 flex-shrink-0`} />
                  <div>
                    <div className="text-[11px] text-text-secondary">{rec.type} / {rec.district}</div>
                    <div className="text-xs">{rec.text}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Info block */}
      <div className="bg-card border border-border rounded-xl p-4 text-[11px] text-text-secondary leading-relaxed">
        <span className="font-medium text-text">Об аналитике: </span>
        Данные демонстрационные (8 районов, 14 дней). AQI (Air Quality Index) — индекс качества воздуха (0-500).
        Risk Score = загруженность x 0.4 + AQI x 0.6. Статусы: норма (&lt;35), внимание (35-60), критично (&gt;60).
      </div>
    </div>
  );
}

function KpiCard({ label, value, sub, status }: { label: string; value: string; sub: string; status: "normal" | "warning" | "critical" }) {
  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <div className="text-[11px] text-text-secondary mb-2">{label}</div>
      <div className={`text-2xl font-semibold ${statusColor[status]}`}>{value}</div>
      <div className="text-[11px] text-text-secondary mt-1">{sub}</div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-bg rounded-lg p-2 text-center">
      <div className="text-xs font-medium">{value}</div>
      <div className="text-[10px] text-text-secondary">{label}</div>
    </div>
  );
}
