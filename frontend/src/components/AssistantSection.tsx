"use client";

import { useState } from "react";
import type { OverviewData } from "@/lib/api";
import AssistantChat from "@/components/AssistantChat";

type SubTab = "chat" | "health" | "routes";

export default function AssistantSection({ data }: { data: OverviewData }) {
  const [tab, setTab] = useState<SubTab>("chat");

  const tabs: { id: SubTab; label: string }[] = [
    { id: "chat", label: "AI-чат" },
    { id: "health", label: "Здоровье" },
    { id: "routes", label: "Маршруты" },
  ];

  const sorted = [...data.districts].sort((a, b) => a.risk_score - b.risk_score);
  const problematic = data.districts.filter((d) => d.avg_congestion >= 60).sort((a, b) => b.avg_congestion - a.avg_congestion);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold mb-1">Помощник</h1>
        <p className="text-sm text-text-secondary">AI-ассистент, здоровье и маршруты</p>
      </div>

      <div className="flex gap-1 bg-card border border-border rounded-lg p-1">
        {tabs.map((t) => (
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

      {tab === "chat" && <AssistantChat />}

      {tab === "health" && (
        <div className="space-y-4">
          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-4">
              Рейтинг районов для прогулок
            </h3>
            <div className="space-y-3">
              {sorted.map((d, i) => {
                const score = Math.max(0, 100 - d.risk_score);
                const color = score >= 60 ? "bg-green" : score >= 40 ? "bg-orange" : "bg-red";
                const textColor = score >= 60 ? "text-green" : score >= 40 ? "text-orange" : "text-red";
                return (
                  <div key={d.district}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold ${textColor} w-5`}>#{i + 1}</span>
                        <span>{d.district}</span>
                      </div>
                      <span className={`text-xs font-medium ${textColor}`}>{score}/100</span>
                    </div>
                    <div className="w-full bg-border rounded-full h-1">
                      <div className={`${color} h-1 rounded-full transition-all`} style={{ width: `${score}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { title: "Для всех", text: "При AQI > 100 сократите время на улице. Лучшее время — утро (до 10:00)." },
              { title: "Группы риска", text: "Дети, пожилые, люди с респираторными заболеваниями — избегайте районов с AQI > 80." },
              { title: "Спортсменам", text: "Бег и велоспорт при AQI < 50. Выбирайте парковые зоны вдали от магистралей." },
            ].map((tip) => (
              <div key={tip.title} className="bg-card border border-border rounded-xl p-4">
                <h4 className="text-sm font-medium mb-2">{tip.title}</h4>
                <p className="text-xs text-text-secondary leading-relaxed">{tip.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "routes" && (
        <div className="space-y-4">
          {problematic.length > 0 ? (
            <div className="bg-card border border-border rounded-xl p-5">
              <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
                Проблемные участки
              </h3>
              <div className="space-y-2">
                {problematic.map((d) => (
                  <div key={d.district} className="flex items-center justify-between p-3 bg-red-bg rounded-lg">
                    <div>
                      <span className="text-sm font-medium">{d.district}</span>
                      <span className="text-xs text-text-secondary ml-2">загруженность {d.avg_congestion}%</span>
                    </div>
                    <a
                      href={`https://2gis.kz/almaty/search/${encodeURIComponent(d.district)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-accent hover:underline"
                    >
                      2GIS
                    </a>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center">
              <p className="text-sm text-text-secondary">Проблемных участков не обнаружено</p>
            </div>
          )}

          <div className="bg-card border border-border rounded-xl p-5">
            <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">Рекомендации</h3>
            <div className="space-y-2">
              {[
                "Избегайте вечерних часов (17:00–20:00) в загруженных районах",
                "Используйте альтернативные маршруты через менее загруженные районы",
                "Проверяйте актуальную обстановку в 2GIS перед выездом",
              ].map((tip, i) => (
                <div key={i} className="flex items-start gap-2 p-2.5 bg-bg rounded-lg">
                  <span className="w-4 h-4 rounded-full bg-accent/20 text-accent flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5">{i + 1}</span>
                  <p className="text-xs text-text-secondary">{tip}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
