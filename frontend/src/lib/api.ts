const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, options);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// ─── Overview ─────────────────────────────────────────────────

export interface OverviewData {
  city_status: "normal" | "warning" | "critical";
  risk_score: number;
  top_kpis: {
    avg_congestion: number;
    avg_aqi: number;
    critical_count: number;
    risk_score: number;
  };
  summary: string;
  severity: string;
  what_is_happening: string;
  why_critical: string;
  ai_powered: boolean;
  districts: DistrictData[];
  top_problem_districts: DistrictData[];
  top_safe_districts: DistrictData[];
  critical_alerts: Issue[];
  recommendations: Recommendation[];
  total_issues: number;
  warning_count: number;
  combined_count: number;
}

export interface DistrictData {
  district: string;
  avg_congestion: number;
  avg_aqi: number;
  avg_speed: number;
  risk_score: number;
  status: "normal" | "warning" | "critical";
  issue_count: number;
  critical_count: number;
  recommendation: string;
}

export function getOverview() {
  return fetchJSON<OverviewData>("/api/overview");
}

// ─── Dashboard (legacy) ──────────────────────────────────────

export interface DashboardData {
  city_status: "normal" | "warning" | "critical";
  total_issues: number;
  critical_count: number;
  transport: {
    kpis: { avg_speed: number; avg_congestion: number; total_incidents: number };
    status: string;
  };
  ecology: {
    kpis: { avg_aqi: number; avg_pm25: number; avg_pm10: number };
    status: string;
  };
  ai_insight: AiInsight;
  issues: Issue[];
  combined_issues: Issue[];
}

export interface AiInsight {
  summary: string;
  severity: string;
  what_is_happening: string;
  why_critical: string;
  top_district: string | null;
  risk_score: number;
  recommendations: Recommendation[];
  total_issues: number;
  critical_count: number;
  warning_count: number;
  combined_count: number;
  ai_powered: boolean;
}

export function getDashboard() {
  return fetchJSON<DashboardData>("/api/dashboard");
}

// ─── Shared types ─────────────────────────────────────────────

export interface Recommendation {
  priority: "high" | "medium" | "low";
  type: string;
  district: string;
  text: string;
}

export interface Issue {
  type: string;
  district: string;
  timestamp: string;
  severity: string;
  description: string;
}

export interface TimeSeriesRecord {
  timestamp: string;
  [key: string]: string | number | undefined;
}

export interface DistrictRecord {
  district: string;
  [key: string]: string | number | undefined;
}

export interface CombinedRecord {
  district: string;
  avg_congestion: number;
  avg_aqi: number;
  risk_score: number;
}

export interface RecyclingPoint {
  name: string;
  lat: number;
  lon: number;
  type: string;
  address: string;
}

export interface ImpactRequest {
  fuel_type: string;
  engine_volume: number;
  daily_km: number;
}

export interface ImpactResult {
  fuel_type: string;
  engine_volume: number;
  daily_km: number;
  co2_per_km: number;
  co2_daily_kg: number;
  co2_monthly_kg: number;
  co2_yearly_kg: number;
  impact_score: number;
  comparison: number;
  level: string;
  explanation: string;
}

// ─── Analytics endpoints ──────────────────────────────────────

export function getCongestionByTime() {
  return fetchJSON<TimeSeriesRecord[]>("/api/transport/congestion-by-time");
}
export function getCongestionByDistrict() {
  return fetchJSON<DistrictRecord[]>("/api/transport/congestion-by-district");
}
export function getAqiByTime() {
  return fetchJSON<TimeSeriesRecord[]>("/api/ecology/aqi-by-time");
}
export function getAqiByDistrict() {
  return fetchJSON<DistrictRecord[]>("/api/ecology/aqi-by-district");
}
export function getCombined() {
  return fetchJSON<CombinedRecord[]>("/api/combined");
}
export function getGeoJSON() {
  return fetchJSON<GeoJSON.FeatureCollection>("/api/geojson");
}
export function getRecycling() {
  return fetchJSON<RecyclingPoint[]>("/api/recycling");
}

// ─── AI & Impact ──────────────────────────────────────────────

export function askAssistant(question: string) {
  return fetchJSON<{ answer: string }>("/api/assistant", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}
export function calculateImpact(data: ImpactRequest) {
  return fetchJSON<ImpactResult>("/api/impact", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}
export function getImpactOptions() {
  return fetchJSON<{ fuel_types: string[]; engine_volumes: number[] }>("/api/impact/options");
}
