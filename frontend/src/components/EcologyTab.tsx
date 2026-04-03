"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Area, AreaChart,
} from "recharts";
import { getAqiByTime, getAqiByDistrict, type TimeSeriesRecord, type DistrictRecord, type Issue } from "@/lib/api";

const tt = { contentStyle: { background: "#131720", border: "1px solid #1e2533", borderRadius: 8, color: "#e2e4e9", fontSize: 12 } };
const tick = { fontSize: 11, fill: "#7a8194" };

export default function EcologyTab({ issues }: { issues: Issue[] }) {
  const [byTime, setByTime] = useState<TimeSeriesRecord[]>([]);
  const [byDistrict, setByDistrict] = useState<DistrictRecord[]>([]);

  useEffect(() => {
    getAqiByTime().then(setByTime);
    getAqiByDistrict().then(setByDistrict);
  }, []);

  const ecoIssues = issues.filter((i) => i.type === "Экология");

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-medium mb-1">AQI по времени</h3>
          <p className="text-[11px] text-text-secondary mb-4">Индекс качества воздуха</p>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={byTime}>
              <defs>
                <linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#34d399" stopOpacity={0.2} />
                  <stop offset="100%" stopColor="#34d399" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1e2533" strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" tick={tick} tickFormatter={(v) => v?.slice(11, 16)} axisLine={false} tickLine={false} />
              <YAxis tick={tick} axisLine={false} tickLine={false} />
              <Tooltip {...tt} />
              <Area type="monotone" dataKey="aqi" stroke="#34d399" strokeWidth={2} fill="url(#ag)" dot={false} name="AQI" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-medium mb-1">AQI по районам</h3>
          <p className="text-[11px] text-text-secondary mb-4">Сравнение</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={byDistrict} layout="vertical">
              <CartesianGrid stroke="#1e2533" strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tick={tick} axisLine={false} tickLine={false} />
              <YAxis dataKey="district" type="category" tick={tick} width={120} axisLine={false} tickLine={false} />
              <Tooltip {...tt} />
              <Bar dataKey="aqi" name="AQI" radius={[0, 6, 6, 0]} barSize={16}>
                {byDistrict.map((e, i) => (
                  <Cell key={i} fill={(e.aqi as number ?? 0) > 100 ? "#f87171" : (e.aqi as number ?? 0) > 50 ? "#fbbf24" : "#34d399"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {ecoIssues.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
            Проблемы экологии ({ecoIssues.length})
          </h3>
          <div className="space-y-1.5 max-h-[300px] overflow-y-auto">
            {ecoIssues.slice(0, 20).map((issue, i) => (
              <div key={i} className={`text-xs p-2.5 rounded-lg ${issue.severity === "critical" ? "bg-red-bg" : "bg-orange-bg"}`}>
                <span className="font-medium">{issue.district}</span>
                <span className="text-text-secondary mx-1.5">{issue.timestamp.slice(5, 16)}</span>
                <span className="text-text-secondary">— {issue.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
