"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Area, AreaChart,
} from "recharts";
import { getCongestionByTime, getCongestionByDistrict, type TimeSeriesRecord, type DistrictRecord, type Issue } from "@/lib/api";

const tt = { contentStyle: { background: "#131720", border: "1px solid #1e2533", borderRadius: 8, color: "#e2e4e9", fontSize: 12 } };
const tick = { fontSize: 11, fill: "#7a8194" };

export default function TransportTab({ issues }: { issues: Issue[] }) {
  const [byTime, setByTime] = useState<TimeSeriesRecord[]>([]);
  const [byDistrict, setByDistrict] = useState<DistrictRecord[]>([]);

  useEffect(() => {
    getCongestionByTime().then(setByTime);
    getCongestionByDistrict().then(setByDistrict);
  }, []);

  const transportIssues = issues.filter((i) => i.type === "Транспорт");

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-medium mb-1">Загруженность по времени</h3>
          <p className="text-[11px] text-text-secondary mb-4">Динамика за период</p>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={byTime}>
              <defs>
                <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#818cf8" stopOpacity={0.2} />
                  <stop offset="100%" stopColor="#818cf8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1e2533" strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" tick={tick} tickFormatter={(v) => v?.slice(11, 16)} axisLine={false} tickLine={false} />
              <YAxis tick={tick} axisLine={false} tickLine={false} />
              <Tooltip {...tt} />
              <Area type="monotone" dataKey="congestion_level" stroke="#818cf8" strokeWidth={2} fill="url(#cg)" dot={false} name="Загруженность %" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-medium mb-1">По районам</h3>
          <p className="text-[11px] text-text-secondary mb-4">Средняя загруженность</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={byDistrict} layout="vertical">
              <CartesianGrid stroke="#1e2533" strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tick={tick} axisLine={false} tickLine={false} />
              <YAxis dataKey="district" type="category" tick={tick} width={120} axisLine={false} tickLine={false} />
              <Tooltip {...tt} />
              <Bar dataKey="congestion_level" name="%" radius={[0, 6, 6, 0]} barSize={16}>
                {byDistrict.map((e, i) => (
                  <Cell key={i} fill={(e.congestion_level as number ?? 0) >= 60 ? "#f87171" : (e.congestion_level as number ?? 0) >= 40 ? "#fbbf24" : "#34d399"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {transportIssues.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
            Проблемы транспорта ({transportIssues.length})
          </h3>
          <div className="space-y-1.5 max-h-[300px] overflow-y-auto">
            {transportIssues.slice(0, 20).map((issue, i) => (
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
