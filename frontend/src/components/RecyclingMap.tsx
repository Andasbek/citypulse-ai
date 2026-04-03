"use client";

import { useEffect, useState } from "react";
import { getRecycling, type RecyclingPoint } from "@/lib/api";

export default function RecyclingMap() {
  const [points, setPoints] = useState<RecyclingPoint[]>([]);

  useEffect(() => {
    getRecycling().then(setPoints);
  }, []);

  return (
    <div className="space-y-4">
      <div className="bg-card border border-border rounded-xl p-5">
        <h3 className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-4">
          Пункты приема вторсырья ({points.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {points.map((point, i) => (
            <div key={i} className="bg-bg border border-border rounded-lg p-4 hover:border-accent/20 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <h4 className="text-sm font-medium">{point.name}</h4>
                <span className="text-[10px] bg-green-bg text-green px-2 py-0.5 rounded-full font-medium flex-shrink-0 ml-2">
                  {point.type}
                </span>
              </div>
              <p className="text-xs text-text-secondary mb-3">{point.address}</p>
              <a
                href={`https://2gis.kz/almaty/geo/${point.lon},${point.lat}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-accent hover:underline"
              >
                Открыть на карте
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
