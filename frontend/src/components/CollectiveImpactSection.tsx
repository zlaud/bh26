"use client";
import { useState } from "react";
import { CollectiveImpact } from "@/lib/types";
import { SCALE_OPTIONS } from "@/lib/constants";

interface Props {
  impact: CollectiveImpact;
}

const SCALE_MULTIPLIERS: Record<string, number> = {
  "100_households": 1,
  "1000_households": 10,
  campus: 12.5,
};

export default function CollectiveImpactModal({ impact }: Props) {
  const [open, setOpen] = useState(false);
  const [scale, setScale] = useState("100_households");
  const multiplier = SCALE_MULTIPLIERS[scale];

  const scaled = {
    savings: Math.round(impact.estimated_savings * multiplier),
    co2: Math.round(impact.co2_saved_kg * multiplier),
    water: Math.round(impact.water_saved_liters * multiplier),
    waste: Math.round(impact.food_waste_reduced_kg * multiplier),
  };

  function fmt(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
    return n.toString();
  }

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-5 bg-gradient-to-r from-green-50 to-emerald-50 border-[1.5px] border-green-200 rounded-2xl hover:border-green-400 hover:-translate-y-0.5 transition-all"
      >
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-green-700 rounded-xl flex items-center justify-center text-lg">
            🌱
          </div>
          <div className="text-left">
            <div className="font-serif text-sm font-medium text-green-900">
              See the community impact
            </div>
            <div className="text-xs text-green-600 mt-0.5">
              What if many households adapted like this?
            </div>
          </div>
        </div>
        <span
          className={`text-green-600 text-lg transition-transform ${open ? "rotate-90" : ""}`}
        >
          ›
        </span>
      </button>

      {open && (
        <div className="mt-4 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex gap-2 mb-4">
            {SCALE_OPTIONS.map((opt) => (
              <button
                key={opt.id}
                onClick={() => setScale(opt.id)}
                className={`text-xs px-4 py-2 rounded-full border transition-all ${
                  scale === opt.id
                    ? "border-green-600 bg-green-50 text-green-700 font-medium"
                    : "border-stone-200 text-stone-500 hover:border-green-300"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-4 gap-3">
            {[
              {
                value: `$${fmt(scaled.savings)}`,
                unit: "Monthly savings",
                equiv: `avg $${Math.round(impact.estimated_savings)} per household`,
              },
              {
                value: `${fmt(scaled.co2)}`,
                unit: "CO₂ avoided (kg)",
                equiv: `≈ ${Math.round(scaled.co2 / 383)} cars off the road`,
              },
              {
                value: `${fmt(scaled.water)}`,
                unit: "Water saved (L)",
                equiv: `≈ ${fmt(Math.round(scaled.water / 340))} person-days`,
              },
              {
                value: `${fmt(scaled.waste)}`,
                unit: "Food waste (kg)",
                equiv: `≈ ${Math.round(scaled.waste / 7.8)} zero-waste homes`,
              },
            ].map((card, i) => (
              <div
                key={i}
                className="bg-white border border-stone-200 rounded-xl p-4 text-center shadow-sm"
              >
                <div className="font-serif text-2xl font-medium text-green-700 mb-1">
                  {card.value}
                </div>
                <div className="font-mono text-xs text-stone-400 uppercase tracking-wide mb-2">
                  {card.unit}
                </div>
                <div className="text-xs text-stone-400 leading-snug">
                  {card.equiv}
                </div>
              </div>
            ))}
          </div>

          <p className="text-xs text-stone-400 mt-3 leading-relaxed">
            Based on: Poore & Nemecek (2018), Mekonnen & Hoekstra (2010), USDA
            ERS (2023), ReFED (2021).{" "}
            <a href="#" className="text-green-700 font-medium hover:underline">
              View methodology →
            </a>
          </p>
        </div>
      )}
    </div>
  );
}
