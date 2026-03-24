"use client";
import { useState } from "react";
import GroceryInput from "@/components/GroceryInput";
import RiskCard from "@/components/RiskCard";
import ResilienceScoreCard from "@/components/ResilienceScoreCard";
import BreakingNewsSimulator from "@/components/BreakingNewsSimulator";
import CollectiveImpactModal from "@/components/CollectiveImpactSection";
import { useDataContext } from "@/context/DataContext";
import { HouseholdResult } from "@/lib/types";

export default function HouseholdPage() {
  const {
    householdData,
    householdLoading,
    householdError,
    analyzeHouseholdGroceries,
  } = useDataContext();

  const [simulatedResult, setSimulatedResult] =
    useState<HouseholdResult | null>(null);
  const [simulated, setSimulated] = useState(false);
  const [currentGroceries, setCurrentGroceries] = useState(
    "tofu, lentils, dried_beans, oats, bananas, spinach, broccoli, olive_oil, white_rice",
  );
  const [currentScaleId] = useState("100_households");
  // Use simulated result when in simulation mode, otherwise use live data
  const displayResult = simulated ? simulatedResult : householdData;

  function handleAnalyze(groceries: string) {
    setCurrentGroceries(groceries);
    setSimulated(false);
    // Always fetch fresh data from the agent
    analyzeHouseholdGroceries(groceries);
  }

  function handleSimulatedHeadline(result: HouseholdResult) {
    setSimulatedResult(result);
    setSimulated(true);
  }

  function handleClearSimulation() {
    setSimulated(false);
  }

  return (
    <main className="max-w-6xl mx-auto px-8 py-10 bg-[var(--bg)] text-[var(--text)]">
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-5 h-0.5 rounded bg-[var(--accent)]" />
          <span className="font-mono text-xs uppercase tracking-widest text-[var(--accent)]">
            household resilience
          </span>
        </div>
        <h1 className="font-serif text-3xl font-medium leading-tight text-[var(--text)]">
          What&apos;s happening to your groceries right now.
        </h1>
        <p className="mt-2 font-light leading-relaxed text-[var(--text2)]">
          Enter your grocery list and we&apos;ll show you which foods face
          supply pressure — and how to adapt before prices change.
        </p>
      </div>

      <div className="space-y-6">
        <GroceryInput onAnalyze={handleAnalyze} loading={householdLoading} />

        {householdError && (
          <div className="rounded-xl p-4 text-sm bg-[var(--red-bg)] border border-[var(--red-border)] text-[var(--red)]">
            {householdError}
          </div>
        )}

        {displayResult && (
          <>
            {simulated && (
              <div className="rounded-xl px-4 py-2 text-xs font-mono bg-[var(--amber-bg)] border border-[var(--amber-border)] text-[var(--amber)]">
                showing simulated headline impact
              </div>
            )}

            <div className="grid grid-cols-[180px_1fr] gap-5">
              <ResilienceScoreCard result={displayResult} />
              <div className="rounded-2xl p-6 shadow-sm border border-[var(--border)] bg-[var(--bg2)] text-[var(--text)]">
                <div className="font-mono text-xs uppercase tracking-wider mb-3 text-[var(--text3)]">
                  Situation summary
                </div>
                <p className="text-sm leading-relaxed font-light mb-4 text-[var(--text)]">
                  {displayResult.summary}
                </p>
                <div className="space-y-2">
                  {(displayResult.patterns || []).map(
                    (p: string, i: number) => (
                      <div
                        key={i}
                        className="flex items-start gap-2 rounded-lg px-3 py-2 bg-[var(--bg3)]"
                      >
                        <div className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 bg-[var(--accent)]" />
                        <span className="text-sm text-[var(--text2)]">{p}</span>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>

            <BreakingNewsSimulator
              groceries={currentGroceries}
              scaleId={currentScaleId}
              onApply={handleSimulatedHeadline}
              onClear={handleClearSimulation}
            />

            <div>
              <div className="font-mono text-xs uppercase tracking-wider mb-3 text-[var(--text3)]">
                Food risk breakdown
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {Object.entries(displayResult.food_risks || {})
                  .sort(
                    ([, a], [, b]) =>
                      (b as { risk_score: number }).risk_score -
                      (a as { risk_score: number }).risk_score,
                  )
                  .map(([food, risk]) => (
                    <RiskCard
                      key={food}
                      food={food}
                      risk={risk as import("@/lib/types").FoodRisk}
                    />
                  ))}
              </div>
            </div>

            <div>
              <div className="font-mono text-xs uppercase tracking-wider mb-3 text-[var(--text3)]">
                Ways to adapt
              </div>
              <div className="grid grid-cols-2 gap-3">
                {(displayResult.strategies || []).map(
                  (
                    s: { type: string; action: string; reason: string },
                    i: number,
                  ) => (
                    <div
                      key={i}
                      className="rounded-2xl p-5 shadow-sm transition-all border border-[var(--border)] bg-[var(--bg2)]"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 rounded-full bg-[var(--accent-light)] border border-[var(--accent)]" />
                        <span className="font-mono text-xs uppercase tracking-wide text-[var(--accent)]">
                          {s.type.replace(/_/g, " ")}
                        </span>
                      </div>
                      <p className="font-serif text-sm font-medium mb-2 leading-snug text-[var(--text)]">
                        {s.action}
                      </p>
                      <p className="text-xs leading-relaxed text-[var(--text2)]">
                        {s.reason}
                      </p>
                    </div>
                  ),
                )}
              </div>
            </div>

            <CollectiveImpactModal impact={displayResult.collective_impact} />
          </>
        )}

        {!displayResult && !householdLoading && (
          <div className="text-center py-20 text-[var(--text3)]">
            <p className="font-serif text-lg text-[var(--text2)]">
              Enter your groceries to see what&apos;s at risk
            </p>
            <p className="text-sm mt-2">Or try a sample basket above</p>
          </div>
        )}

        {householdLoading && (
          <div className="text-center py-20">
            <div className="inline-flex items-center gap-3 text-[var(--text2)]">
              <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin border-[var(--accent)] border-t-transparent" />
              <span className="font-serif text-sm">
                Analyzing your basket...
              </span>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
