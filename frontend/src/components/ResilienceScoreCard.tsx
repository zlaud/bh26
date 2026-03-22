import { HouseholdResult } from "@/lib/types";

interface Props {
  result: HouseholdResult;
}

function getScore(result: HouseholdResult): number {
  const risks = Object.values(result.food_risks || {});
  if (!risks.length) return 100;
  const avg = risks.reduce((sum, r) => sum + r.risk_score, 0) / risks.length;
  return Math.round((1 - avg) * 100);
}

export default function ResilienceScoreCard({ result }: Props) {
  const score = getScore(result);
  const color =
    score >= 70
      ? "text-green-700"
      : score >= 40
        ? "text-amber-600"
        : "text-red-600";
  const label =
    score >= 70
      ? "good resilience"
      : score >= 40
        ? "moderate risk"
        : "high risk";
  const circumference = 2 * Math.PI * 34;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm flex flex-col items-center gap-3">
      <div className="relative w-20 h-20">
        <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
          <circle
            cx="40"
            cy="40"
            r="34"
            fill="none"
            stroke="#f5f0e8"
            strokeWidth="6"
          />
          <circle
            cx="40"
            cy="40"
            r="34"
            fill="none"
            stroke={
              score >= 70 ? "#15803d" : score >= 40 ? "#d97706" : "#dc2626"
            }
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000"
          />
        </svg>
        <div
          className={`absolute inset-0 flex items-center justify-center font-serif text-xl font-medium ${color}`}
        >
          {score}
        </div>
      </div>
      <div className="text-center">
        <div className="text-xs text-stone-400 font-medium uppercase tracking-wide">
          Resilience score
        </div>
        <div className={`text-xs font-medium mt-1 ${color}`}>{label}</div>
      </div>
    </div>
  );
}
