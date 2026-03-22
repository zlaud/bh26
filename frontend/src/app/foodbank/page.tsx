"use client";
import { useState } from "react";
import { useDataContext } from "@/context/DataContext";
import { RISK_COLORS, URGENCY_COLORS } from "@/lib/constants";

interface TopRisk {
  food: string;
  risk_label: string;
  trajectory: string;
}

function RiskCardExpand({ risk }: { risk: TopRisk }) {
  const [expanded, setExpanded] = useState(false);
  const colors =
    RISK_COLORS[risk.risk_label as keyof typeof RISK_COLORS] ||
    RISK_COLORS.MEDIUM;

  return (
    <div
      className={`bg-white rounded-xl border-[1.5px] ${colors?.border || "border-stone-200"} p-4`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="font-serif text-sm font-medium text-stone-800 capitalize">
          {risk.food.replace(/_/g, " ")}
        </span>
        <span
          className={`font-mono text-[10px] px-2 py-0.5 rounded-full ${colors?.badge || "bg-stone-50 text-stone-700"}`}
        >
          {risk.risk_label}
        </span>
      </div>
      <div
        className={`text-xs text-stone-500 leading-snug ${expanded ? "" : "line-clamp-2"}`}
      >
        {risk.trajectory}
      </div>
      {risk.trajectory && risk.trajectory.length > 80 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-green-700 hover:text-green-800 mt-2 font-medium"
        >
          {expanded ? "Show less" : "Read more"}
        </button>
      )}
    </div>
  );
}

export default function FoodbankPage() {
  const {
    foodbankData: result,
    foodbankLoading: loading,
    foodbankError: error,
  } = useDataContext();

  if (loading)
    return (
      <main className="max-w-6xl mx-auto px-8 py-10">
        <div className="flex items-start justify-between mb-10">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-5 h-0.5 bg-[var(--accent)] rounded" />
              <span className="font-mono text-xs uppercase tracking-widest text-[var(--accent)]">
                food bank operations
              </span>
            </div>
            <h1 className="font-serif text-3xl font-medium text-[var(--text)] leading-tight">
              Current pressures and what to do this week.
            </h1>
            <p className="text-[var(--text2)] mt-2 font-light">
              Forward-looking operational guidance based on live food system
              signals.
            </p>
          </div>
          <div className="bg-[var(--accent-light)] border border-[var(--green-border)] rounded-full px-4 py-2 font-mono text-xs text-[var(--accent)]">
            national · live signals
          </div>
        </div>

        <div className="bg-[var(--bg2)] rounded-2xl border border-[var(--border)] p-6 shadow-sm mb-6 animate-pulse">
          <div className="h-4 bg-[var(--bg3)] rounded w-32 mb-3" />
          <div className="h-3 bg-[var(--bg3)] rounded w-full mb-2" />
          <div className="h-3 bg-[var(--bg3)] rounded w-3/4" />
        </div>

        <div className="h-4 bg-[var(--bg3)] rounded w-48 mb-3" />
        <div className="flex flex-wrap gap-3 mb-8">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-[var(--bg2)] rounded-xl border border-[var(--border)] p-4 min-w-[140px] animate-pulse"
            >
              <div className="h-5 bg-[var(--bg3)] rounded w-16 mb-2" />
              <div className="h-4 bg-[var(--bg3)] rounded w-20 mb-1" />
              <div className="h-3 bg-[var(--bg3)] rounded w-24" />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="h-4 bg-[var(--bg3)] rounded w-40 mb-3" />
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div
                  key={i}
                  className="bg-[var(--bg2)] border border-[var(--border)] rounded-xl p-4 animate-pulse"
                >
                  <div className="h-3 bg-[var(--bg3)] rounded w-20 mb-2" />
                  <div className="h-4 bg-[var(--bg3)] rounded w-full mb-1" />
                  <div className="h-3 bg-[var(--bg3)] rounded w-3/4" />
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="h-4 bg-[var(--bg3)] rounded w-40 mb-3" />
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div
                  key={i}
                  className="bg-[var(--bg2)] border border-[var(--border)] rounded-xl p-4 animate-pulse"
                >
                  <div className="h-3 bg-[var(--bg3)] rounded w-32 mb-2" />
                  <div className="h-3 bg-[var(--bg3)] rounded w-full" />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-center mt-8 gap-3 text-[var(--text2)]">
          <div className="w-5 h-5 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin" />
          <span className="font-serif text-sm">
            Analyzing food system signals...
          </span>
        </div>
      </main>
    );

  if (error)
    return (
      <div className="max-w-6xl mx-auto px-8 py-10">
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          {error}
        </div>
      </div>
    );

  if (!result) return null;

  return (
    <main className="max-w-6xl mx-auto px-8 py-10">
      <div className="flex items-start justify-between mb-10">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-5 h-0.5 bg-green-700 rounded" />
            <span className="font-mono text-xs uppercase tracking-widest text-green-700">
              food bank operations
            </span>
          </div>
          <h1 className="font-serif text-3xl font-medium text-stone-800 leading-tight">
            Current pressures and what to do this week.
          </h1>
          <p className="text-stone-500 mt-2 font-light">
            Forward-looking operational guidance based on live food system
            signals.
          </p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-full px-4 py-2 font-mono text-xs text-green-700">
          national · live signals
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm mb-6">
        <div className="font-mono text-xs uppercase tracking-wider text-stone-400 mb-3">
          Situation summary
        </div>
        <p className="text-sm text-stone-700 leading-relaxed font-light">
          {result.summary}
        </p>
      </div>

      <div className="font-mono text-xs uppercase tracking-wider text-stone-400 mb-3">
        Top foods at risk this week
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-8">
        {(result.top_risks || []).map((risk, i) => (
          <RiskCardExpand key={i} risk={risk} />
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <div className="font-mono text-xs uppercase tracking-wider text-stone-400 mb-3">
            Procurement actions
          </div>
          <div className="space-y-3">
            {(result.procurement_actions || []).map((action, i) => (
              <div
                key={i}
                className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm hover:border-stone-300 transition-all"
              >
                <div className="flex items-start gap-4">
                  <span className="font-serif text-xl font-medium text-stone-200 flex-shrink-0 pt-0.5">
                    {action.priority}
                  </span>
                  <div>
                    <div
                      className={`font-mono text-xs uppercase tracking-wide mb-1 ${URGENCY_COLORS[action.urgency] || "text-stone-600"}`}
                    >
                      {action.urgency}
                    </div>
                    <p className="font-serif text-sm font-medium text-stone-800 mb-1 leading-snug">
                      {action.action}
                    </p>
                    <p className="text-xs text-stone-500 leading-relaxed">
                      {action.reason}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="font-mono text-xs uppercase tracking-wider text-stone-400 mb-3">
            Substitution actions
          </div>
          <div className="space-y-3">
            {(result.substitution_actions || []).map((sub, i) => (
              <div
                key={i}
                className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm hover:border-stone-300 transition-all"
              >
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="font-mono text-xs bg-red-50 border border-red-200 text-red-700 px-2 py-0.5 rounded">
                    {sub.from}
                  </span>
                  <span className="text-stone-400">→</span>
                  <span className="font-mono text-xs bg-green-50 border border-green-200 text-green-700 px-2 py-0.5 rounded">
                    {sub.to}
                  </span>
                  <span
                    className={`font-mono text-xs ml-auto ${URGENCY_COLORS[sub.urgency] || "text-stone-600"}`}
                  >
                    {sub.urgency}
                  </span>
                </div>
                <p className="text-xs text-stone-500 leading-relaxed">
                  {sub.reason}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {(result.patterns || []).length > 0 && (
        <div className="mt-6 bg-white border border-stone-200 rounded-2xl p-5 shadow-sm">
          <div className="font-mono text-xs uppercase tracking-wider text-stone-400 mb-3">
            Category patterns
          </div>
          <div className="space-y-2">
            {(result.patterns || []).map((p, i) => (
              <div key={i} className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-600 mt-1.5 flex-shrink-0" />
                <span className="text-sm text-stone-600">{p}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
