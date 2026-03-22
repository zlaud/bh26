"use client";
import { useState } from "react";
import { HouseholdResult, SimulatedHeadline } from "@/lib/types";
import { useDataContext } from "@/context/DataContext";
import simulatedHeadlines from "@/data/simulated_headlines.json";

interface Props {
  groceries: string;
  scaleId: string;
  onApply: (result: HouseholdResult) => void;
  onClear: () => void;
}

const headlines = simulatedHeadlines.headlines as SimulatedHeadline[];

export default function BreakingNewsSimulator({
  groceries,
  scaleId,
  onApply,
  onClear,
}: Props) {
  const { simulateHeadlineWithCache, simulationLoading } = useDataContext();
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleClick(headline: SimulatedHeadline) {
    if (activeId === headline.id) {
      setActiveId(null);
      onClear();
      return;
    }

    setActiveId(headline.id);
    setLoading(true);

    try {
      const result = await simulateHeadlineWithCache(
        headline.id,
        groceries,
        headline.signal,
        scaleId,
      );
      await new Promise((resolve) => setTimeout(resolve, 400));
      onApply(result);
    } catch (e) {
      console.error("Simulation failed:", e);
      setActiveId(null);
    } finally {
      setLoading(false);
    }
  }

  const active = headlines.find((h) => h.id === activeId);

  return (
    <div className="mb-7">
      <div className="text-[12px] font-medium uppercase tracking-[0.05em] text-stone-500 mb-[14px]">
        Simulate breaking news
      </div>

      <div className="flex gap-2 flex-wrap">
        {headlines.map((h) => (
          <button
            key={h.id}
            onClick={() => !loading && handleClick(h)}
            disabled={loading}
            className={`flex items-center gap-2 text-[12px] px-4 py-[10px] rounded-[10px] border-[1.5px] transition-all duration-200 max-w-[260px] text-left leading-snug ${
              activeId === h.id && loading
                ? "border-[#f5d9b8] bg-[#fdf6ee] text-[#b7641a] opacity-70"
                : activeId === h.id
                  ? "border-[#f5d9b8] bg-[#fdf6ee] text-[#b7641a]"
                  : "border-black/[0.14] bg-white text-stone-500 hover:border-[#f5d9b8] hover:bg-[#fdf6ee] hover:-translate-y-px disabled:opacity-40 disabled:cursor-not-allowed"
            }`}
          >
            <span className="text-[14px] flex-shrink-0">
              {activeId === h.id && loading ? "⏳" : h.icon}
            </span>
            <span>{h.headline}</span>
          </button>
        ))}
      </div>

      {active && (
        <div className="mt-3 flex items-center gap-3 bg-[#fdf6ee] border-[1.5px] border-[#f5d9b8] rounded-[10px] px-[18px] py-[14px]">
          <span className="font-mono text-[10px] font-medium bg-[rgba(183,100,26,0.12)] border border-[#f5d9b8] text-[#b7641a] px-2 py-[3px] rounded tracking-wider whitespace-nowrap">
            {loading ? "ANALYZING..." : "BREAKING"}
          </span>
          <span className="text-[13px] text-stone-700">{active.headline}</span>
          <span className="font-mono text-[11px] text-stone-400 ml-auto whitespace-nowrap">
            {active.source} · {active.published_at}
          </span>
        </div>
      )}

      {activeId && !loading && (
        <div className="mt-2 flex items-center gap-2 font-mono text-[11px] text-[#b7641a] bg-[rgba(183,100,26,0.06)] border border-[#f5d9b8] rounded-lg px-[14px] py-2">
          ⚡ showing simulated headline impact — click headline again to clear
        </div>
      )}
    </div>
  );
}
