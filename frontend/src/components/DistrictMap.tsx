"use client";

import type { DistrictData } from "@/lib/api";

// Simplified SVG map positions for 8 Almaty districts
const districtPositions: Record<string, { x: number; y: number; w: number; h: number }> = {
  "Наурызбайский": { x: 20, y: 120, w: 110, h: 90 },
  "Алатауский":    { x: 50, y: 220, w: 110, h: 80 },
  "Ауэзовский":    { x: 140, y: 100, w: 100, h: 100 },
  "Бостандыкский":  { x: 240, y: 140, w: 110, h: 100 },
  "Алмалинский":    { x: 320, y: 70, w: 100, h: 90 },
  "Медеуский":      { x: 360, y: 160, w: 120, h: 90 },
  "Жетысуский":     { x: 400, y: 40, w: 110, h: 80 },
  "Турксибский":    { x: 490, y: 70, w: 100, h: 90 },
};

function riskColor(status: string): string {
  if (status === "critical") return "#f87171";
  if (status === "warning") return "#fbbf24";
  return "#34d399";
}

function riskBg(status: string): string {
  if (status === "critical") return "rgba(248,113,113,0.15)";
  if (status === "warning") return "rgba(251,191,36,0.1)";
  return "rgba(52,211,153,0.08)";
}

export default function DistrictMap({
  districts,
  selected,
  onSelect,
}: {
  districts: DistrictData[];
  selected: DistrictData | null;
  onSelect: (d: DistrictData) => void;
}) {
  return (
    <svg viewBox="0 0 620 320" className="w-full h-auto" style={{ minHeight: 260 }}>
      {districts.map((d) => {
        const pos = districtPositions[d.district];
        if (!pos) return null;
        const isSelected = selected?.district === d.district;
        const color = riskColor(d.status);
        const bg = riskBg(d.status);

        return (
          <g
            key={d.district}
            onClick={() => onSelect(d)}
            className="cursor-pointer"
          >
            <rect
              x={pos.x}
              y={pos.y}
              width={pos.w}
              height={pos.h}
              rx={10}
              fill={bg}
              stroke={isSelected ? color : "rgba(255,255,255,0.06)"}
              strokeWidth={isSelected ? 2 : 1}
              className="transition-all duration-200 hover:opacity-80"
            />
            <text
              x={pos.x + pos.w / 2}
              y={pos.y + pos.h / 2 - 8}
              textAnchor="middle"
              fill="currentColor"
              fontSize="11"
              fontWeight="500"
              className="pointer-events-none"
            >
              {d.district.length > 12 ? d.district.slice(0, 11) + "." : d.district}
            </text>
            <text
              x={pos.x + pos.w / 2}
              y={pos.y + pos.h / 2 + 10}
              textAnchor="middle"
              fill={color}
              fontSize="16"
              fontWeight="700"
              className="pointer-events-none"
            >
              {d.risk_score}
            </text>
            <text
              x={pos.x + pos.w / 2}
              y={pos.y + pos.h / 2 + 25}
              textAnchor="middle"
              fill="var(--text-secondary)"
              fontSize="9"
              className="pointer-events-none"
            >
              risk score
            </text>
          </g>
        );
      })}
    </svg>
  );
}
