import {
  HouseholdResult,
  FoodbankResult,
  PipelineStatus,
  SimulatedHeadline,
} from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export async function analyzeHousehold(
  groceries: string,
  scale_id: string = "100_households",
): Promise<HouseholdResult> {
  return request<HouseholdResult>("/api/household/analyze", {
    method: "POST",
    body: JSON.stringify({ groceries, scale_id }),
  });
}

export async function simulateHeadline(
  groceries: string,
  signal: SimulatedHeadline["signal"],
  scale_id: string = "100_households",
): Promise<HouseholdResult> {
  return request<HouseholdResult>("/api/pipeline/simulate-headline", {
    method: "POST",
    body: JSON.stringify({ groceries, signal, scale_id }),
  });
}

export async function getFoodbankDashboard(
  region: string = "national",
): Promise<FoodbankResult> {
  return request<FoodbankResult>(`/api/foodbank/dashboard?region=${region}`);
}

export async function getGlobalRisks(): Promise<Record<string, any>> {
  const data = await request<{ risks: Record<string, any> }>(
    "/api/pipeline/risks/global",
  );
  return data.risks;
}

export async function getPipelineStatus(): Promise<PipelineStatus> {
  return request<PipelineStatus>("/api/pipeline/status");
}

export async function runFullPipeline(days_back: number = 7) {
  return request("/api/pipeline/run-all", {
    method: "POST",
    body: JSON.stringify({ days_back }),
  });
}
