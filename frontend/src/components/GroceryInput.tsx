"use client";
import { useState } from "react";
import { SAMPLE_BASKETS } from "@/lib/constants";

interface Props {
  onAnalyze: (groceries: string) => void;
  loading: boolean;
}

export default function GroceryInput({ onAnalyze, loading }: Props) {
  const [value, setValue] = useState(
    "tofu, lentils, dried_beans, oats, bananas, spinach, broccoli, olive_oil, white_rice",
  );

  return (
    <div
      style={{
        background: "var(--bg2)",
        border: "1px solid var(--border)",
        borderRadius: "16px",
        padding: "28px",
        marginBottom: "28px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.04)",
      }}
    >
      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-3">
        Your grocery list
      </label>
      <div className="flex gap-3">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="eggs, bananas, rice, milk..."
          className="flex-1 bg-[var(--bg)] border-[1.5px] border-stone-200 rounded-xl px-4 py-3 text-sm text-stone-800 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-600/10 transition-all"
        />
        <button
          onClick={() => onAnalyze(value)}
          disabled={loading}
          className="bg-[var(--accent)] disabled:opacity-60 text-white rounded-xl px-6 py-3 text-sm font-medium transition-all hover:-translate-y-0.5 hover:shadow-md"
        >
          {loading ? "Analyzing..." : "Analyze basket →"}
        </button>
      </div>
      <div className="flex items-center gap-2 mt-3 flex-wrap">
        <span className="text-xs text-stone-400">Try a sample:</span>
        {Object.entries(SAMPLE_BASKETS).map(([key, val]) => (
          <button
            key={key}
            onClick={() => setValue(val)}
            className="text-xs bg-[var(--bg)] hover:bg-green-50 border border-stone-200 hover:border-green-300 hover:text-green-700 text-stone-500 rounded-full px-3 py-1 transition-all"
          >
            {key === "family"
              ? "Family"
              : key === "budget"
                ? "Budget"
                : "Plant-based"}
          </button>
        ))}
      </div>
    </div>
  );
}
