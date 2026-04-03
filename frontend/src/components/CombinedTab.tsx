"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell, ZAxis, LabelList,
} from "recharts";
import { getCombined, type CombinedRecord, type Issue } from "@/lib/api";

const tt = { contentStyle: { background: "#131720", border: "1px solid #1e2533", borderRadius: 8, color: "#e2e4e9", fontSize: 12 } };
const tick = { fontSize: 11, fill: "#7a8194" };

function riskFill(score: number) {
  return score > 60 ? "#f87171" : score > 35 ? "#fbbf24" : "#34d399";
}

export default function CombinedTab({ combinedIssues }: { combinedIssues: Issue[] }) {
  const [data, setData] = useState<CombinedRecord[]>([]);

  useEffect(() => {
    getCombined().then(setData);
  }, []);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-medium mb-1">Risk Score по районам</h3>
          <p className="text-[11px] text-text-secondary mb-4">congestion x 0.4 + AQI x 0.6</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data}>
              <CartesianGrid stroke="#1e2533" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="district" tick={{ fontSize: 9, fill: "#7a8194" }} axisLine={false} tickLine={false} />
              <YAxis tick={tick} axisLine={false} tickLine={false} />
              <Tooltip {...tt} />
              <Bar dataKey="risk_score" name="Risk" radius={[6, 6, 0, 0]} barSize={32}>
                {data.map((e, i) => <Cell key={i} fill={riskFill(e.risk_score)} />)}
                <LabelList dataKey="risk_score" position="top" fontSize={10} fill="#7a8194" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-medium mb-1">Загруженность vs AQI</h3>
          <p className="text-[11px] text-text-secondary mb-4">Размер = risk score</p>
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart>
              <CartesianGrid stroke="#1e2533" strokeDasharray="3 3" />
              <XAxis dataKey="avg_congestion" name="Загруженность" unit="%" tick={tick} axisLine={false} tickLine={false} />
              <YAxis dataKey="avg_aqi" name="AQI" tick={tick} axisLine={false} tickLine={false} />
              <ZAxis dataKey="risk_score" range={[80, 500]} name="Risk" />
              <Tooltip {...tt} />
              <Scatter data={data} name="Районы">
                {data.map((e, i) => <Cell key={i} fill={riskFill(e.risk_score)} />)}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {combinedIssues.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
            Комбинированные проблемы ({combinedIssues.length})
          </h3>
          <div className="space-y-1.5 max-h-[200px] overflow-y-auto">
            {combinedIssues.map((issue, i) => (
              <div key={i} className="text-xs p-2.5 rounded-lg bg-red-bg">
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
