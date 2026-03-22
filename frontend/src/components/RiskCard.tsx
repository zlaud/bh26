"use client";
import { useState } from "react";
import { FoodRisk } from "@/lib/types";
import { RISK_COLORS } from "@/lib/constants";

interface Props {
  food: string;
  risk: FoodRisk;
}

export default function RiskCard({ food, risk }: Props) {
  const [open, setOpen] = useState(false);
  const colors = RISK_COLORS[risk.risk_label];

  return (
    <div
      className={`bg-white rounded-2xl p-5 border-[1.5px] ${colors.border} shadow-sm hover:-translate-y-1 transition-all duration-200`}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="font-serif text-base font-medium text-stone-800 capitalize">
          {risk.label || food.replace(/_/g, " ")}
        </span>
        <span
          className={`font-mono text-xs px-2 py-1 rounded-full ${colors.badge}`}
        >
          {risk.risk_label}
        </span>
      </div>

      <div className="h-1 bg-stone-100 rounded-full mb-3 overflow-hidden">
        <div
          className={`h-full rounded-full ${colors.bar} transition-all duration-700`}
          style={{ width: `${risk.risk_score * 100}%` }}
        />
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {[
          ...new Set(
            (risk.top_drivers || []).map((driver) =>
              typeof driver === "string"
                ? driver
                : (driver as { driver: string }).driver,
            ),
          ),
        ].map((driverText, idx) => (
          <span
            key={idx}
            className="font-mono text-xs text-stone-400 bg-stone-50 border border-stone-200 rounded px-1.5 py-0.5"
          >
            {driverText}
          </span>
        ))}
      </div>

      <button
        onClick={() => setOpen(!open)}
        className="text-xs text-stone-400 hover:text-green-700 transition-colors flex items-center gap-1"
      >
        <span className={`transition-transform ${open ? "rotate-90" : ""}`}>
          ›
        </span>
        See why
      </button>

      {open && (
        <div className="mt-3 pt-3 border-t border-stone-100 space-y-3">
          {(risk.evidence || []).map((e, i) => (
            <div key={i}>
              <p className="text-xs font-medium text-stone-700 mb-0.5 leading-snug">
                {e.source_title}
              </p>
              <p className="font-mono text-xs text-stone-400">
                {e.source_name} · {e.source_date?.slice(0, 10)}
              </p>
              <p className="text-xs text-stone-500 mt-1 italic leading-relaxed">
                {e.short_explanation}
              </p>
            </div>
          ))}
          {(risk.evidence || []).length === 0 &&
            (risk.semantic_evidence || []).length > 0 && (
              <>
                {(risk.semantic_evidence || []).map((e, i) => (
                  <div key={i}>
                    <p className="text-xs font-medium text-stone-700 mb-0.5 leading-snug">
                      {(e as unknown as { headline?: string }).headline ||
                        e.title ||
                        "Related evidence"}
                    </p>
                    <p className="font-mono text-xs text-stone-400">
                      {e.source || "Source"}
                    </p>
                  </div>
                ))}
              </>
            )}
          {(risk.evidence || []).length > 0 &&
            (risk.semantic_evidence || []).length > 0 && (
              <div className="mt-2 pt-2 border-t border-stone-100">
                <p className="font-mono text-xs text-stone-400 mb-2">
                  semantically related
                </p>
                {(risk.semantic_evidence || []).map((e, i) => (
                  <div key={i} className="mb-2">
                    <p className="text-xs text-stone-600 leading-snug">
                      {e.title}
                    </p>
                    <p className="font-mono text-xs text-stone-400">
                      {e.source}
                    </p>
                  </div>
                ))}
              </div>
            )}
        </div>
      )}
    </div>
  );
}
