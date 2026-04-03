"use client";

import { useEffect, useState } from "react";
import { getImpactOptions, calculateImpact, type ImpactResult } from "@/lib/api";

const levelCfg: Record<string, { label: string; color: string }> = {
  low: { label: "Низкий", color: "text-green" },
  medium: { label: "Средний", color: "text-orange" },
  high: { label: "Высокий", color: "text-red" },
};

const selectClass = "w-full px-3 py-2 rounded-lg bg-bg border border-border text-sm focus:outline-none focus:border-accent/40 transition-colors";

export default function ImpactCalculator() {
  const [fuelTypes, setFuelTypes] = useState<string[]>([]);
  const [engineVolumes, setEngineVolumes] = useState<number[]>([]);
  const [fuelType, setFuelType] = useState("");
  const [engineVolume, setEngineVolume] = useState(0);
  const [dailyKm, setDailyKm] = useState(35);
  const [result, setResult] = useState<ImpactResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getImpactOptions().then((opts) => {
      setFuelTypes(opts.fuel_types);
      setEngineVolumes(opts.engine_volumes);
      setFuelType(opts.fuel_types[0]);
      setEngineVolume(opts.engine_volumes[3]);
    });
  }, []);

  async function handleCalculate() {
    setLoading(true);
    try {
      setResult(await calculateImpact({ fuel_type: fuelType, engine_volume: engineVolume, daily_km: dailyKm }));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-xl p-5">
        <h3 className="text-sm font-medium mb-4">Параметры автомобиля</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-[11px] text-text-secondary mb-1.5">Тип топлива</label>
            <select value={fuelType} onChange={(e) => setFuelType(e.target.value)} className={selectClass}>
              {fuelTypes.map((ft) => <option key={ft} value={ft}>{ft}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-[11px] text-text-secondary mb-1.5">Объем двигателя</label>
            <select value={engineVolume} onChange={(e) => setEngineVolume(Number(e.target.value))} className={selectClass}>
              {engineVolumes.map((v) => <option key={v} value={v}>{v} л</option>)}
            </select>
          </div>
          <div>
            <label className="block text-[11px] text-text-secondary mb-1.5">Пробег в день (км)</label>
            <input type="number" value={dailyKm} onChange={(e) => setDailyKm(Number(e.target.value))} className={selectClass} />
          </div>
        </div>
        <button
          onClick={handleCalculate}
          disabled={loading}
          className="px-5 py-2 rounded-lg bg-accent text-white text-sm font-medium disabled:opacity-30 transition-opacity"
        >
          {loading ? "Расчет..." : "Рассчитать"}
        </button>
      </div>

      {result && (() => {
        const cfg = levelCfg[result.level] || levelCfg.low;
        return (
          <div className="bg-card border border-border rounded-xl p-5">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-sm font-medium">Air Impact Score</h3>
              <div className={`text-2xl font-semibold ${cfg.color}`}>
                {result.impact_score}<span className="text-xs font-normal text-text-secondary">/100</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {[
                { v: result.co2_per_km, l: "г CO\u2082/км" },
                { v: result.co2_daily_kg, l: "кг/день" },
                { v: result.co2_monthly_kg, l: "кг/мес" },
                { v: result.co2_yearly_kg, l: "кг/год" },
              ].map((s) => (
                <div key={s.l} className="bg-bg rounded-lg p-3 text-center">
                  <div className="text-sm font-medium">{s.v}</div>
                  <div className="text-[10px] text-text-secondary mt-0.5">{s.l}</div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-3 p-3 bg-bg rounded-lg text-xs mb-4">
              <span className={`font-medium ${cfg.color}`}>{cfg.label}</span>
              <span className="text-text-secondary">
                {result.comparison > 0 ? "+" : ""}{result.comparison}% к среднему по Алматы
              </span>
            </div>

            {result.explanation && (
              <div className="p-3 bg-accent-bg rounded-lg border border-accent/10">
                <div className="text-[11px] font-medium text-accent mb-1">AI-интерпретация</div>
                <p className="text-xs text-text-secondary leading-relaxed">{result.explanation}</p>
              </div>
            )}

            <div className="mt-4 p-3 bg-bg rounded-lg text-[11px] text-text-secondary leading-relaxed">
              <span className="font-medium text-text">Как считается: </span>
              Impact Score = отношение вашего CO2 к среднему по Алматы (5.5 кг/день), масштабированное 0-100.
            </div>
          </div>
        );
      })()}
    </div>
  );
}
