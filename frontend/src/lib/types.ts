export type RiskLabel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type TimeHorizon = "emerging" | "active" | "sustained";
export type Urgency = "critical" | "immediate" | "watch";
export type StrategyType =
  | "reduce_reliance"
  | "diversify"
  | "timing_adjustment"
  | "partial_substitution"
  | "flexible_consumption";

export interface Evidence {
  event_type: string;
  short_explanation: string;
  source_title: string;
  source_name: string;
  source_date: string;
  source_url: string;
  title?: string;
  source?: string;
  published_at?: string;
}

export interface SemanticEvidence {
  title: string;
  source: string;
  published_at: string;
  relevance_score: number;
}

export interface FoodRisk {
  food: string;
  label: string;
  risk_score: number;
  risk_label: RiskLabel;
  top_drivers: string[];
  supporting_articles: string[];
  evidence: Evidence[];
  semantic_evidence: SemanticEvidence[];
}

export interface TopRisk {
  food: string;
  risk_label: RiskLabel;
  time_horizon: TimeHorizon;
  why: string;
}

export interface Strategy {
  type: StrategyType;
  action: string;
  reason: string;
}

export interface Recommendation {
  food: string;
  action: string;
  why: string;
  estimated_monthly_savings: number;
}

export interface EvidencePanel {
  food: string;
  drivers: string[];
  headlines: string[];
}

export interface CollectiveImpact {
  scale_label: string;
  estimated_savings: number;
  co2_saved_kg: number;
  water_saved_liters: number;
  food_waste_reduced_kg: number;
}

export interface HouseholdResult {
  summary: string;
  top_risks: TopRisk[];
  patterns: string[];
  strategies: Strategy[];
  recommendations: Recommendation[];
  evidence_panel: EvidencePanel[];
  collective_impact: CollectiveImpact;
  impact_explanation: {
    summary: string;
    assumptions: string[];
  };
  user_foods: string[];
  food_risks: Record<string, FoodRisk>;
  error?: string;
}

export interface FoodbankTopRisk {
  food: string;
  risk_label: RiskLabel;
  current_state: string;
  time_horizon: TimeHorizon;
  trajectory: string;
}

export interface ProcurementAction {
  priority: number;
  urgency: Urgency;
  action: string;
  reason: string;
}

export interface SubstitutionAction {
  from: string;
  to: string;
  urgency: Urgency;
  action: string;
  reason: string;
}

export interface FoodbankResult {
  summary: string;
  top_risks: FoodbankTopRisk[];
  patterns: string[];
  procurement_actions: ProcurementAction[];
  substitution_actions: SubstitutionAction[];
  error?: string;
}

export interface SimulatedHeadline {
  id: string;
  headline: string;
  subheadline: string;
  source: string;
  published_at: string;
  icon: string;
  signal: {
    event_type: string;
    severity: number;
    confidence: number;
    region: string;
    affected_supply_chain: string;
    short_explanation: string;
  };
}

export interface PipelineStatus {
  articles: number;
  signals: number;
  food_risks: number;
}
