"use client";
import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import {
  getFoodbankDashboard,
  analyzeHousehold,
  simulateHeadline,
} from "@/lib/api";
import {
  FoodbankResult,
  HouseholdResult,
  SimulatedHeadline,
} from "@/lib/types";
import { SAMPLE_BASKETS } from "@/lib/constants";
import simulatedHeadlinesData from "@/data/simulated_headlines.json";

const HEADLINES = simulatedHeadlinesData.headlines as SimulatedHeadline[];

interface DataContextType {
  foodbankData: FoodbankResult | null;
  foodbankLoading: boolean;
  foodbankError: string | null;
  refetchFoodbank: () => void;
  householdData: HouseholdResult | null;
  householdLoading: boolean;
  householdError: string | null;
  analyzeHouseholdGroceries: (groceries: string, scaleId?: string) => void;
  simulatedResults: Record<string, HouseholdResult>;
  simulateHeadlineWithCache: (
    headlineId: string,
    groceries: string,
    signal: SimulatedHeadline["signal"],
    scaleId?: string,
  ) => Promise<HouseholdResult>;
  simulationLoading: boolean;
}

const DataContext = createContext<DataContextType | null>(null);

export function DataProvider({ children }: { children: ReactNode }) {
  const [foodbankData, setFoodbankData] = useState<FoodbankResult | null>(null);
  const [foodbankLoading, setFoodbankLoading] = useState(true);
  const [foodbankError, setFoodbankError] = useState<string | null>(null);

  const [householdData, setHouseholdData] = useState<HouseholdResult | null>(
    null,
  );
  const [householdLoading, setHouseholdLoading] = useState(true);
  const [householdError, setHouseholdError] = useState<string | null>(null);

  const [simulatedResults, setSimulatedResults] = useState<
    Record<string, HouseholdResult>
  >({});
  const [simulationLoading, setSimulationLoading] = useState(false);

  const simulateHeadlineWithCache = async (
    headlineId: string,
    groceries: string,
    signal: SimulatedHeadline["signal"],
    scaleId: string = "100_households",
  ): Promise<HouseholdResult> => {
    const cacheKey = `${headlineId}:${groceries}:${scaleId}`;

    if (simulatedResults[cacheKey]) {
      return simulatedResults[cacheKey];
    }

    setSimulationLoading(true);
    try {
      const result = await simulateHeadline(groceries, signal, scaleId);
      setSimulatedResults((prev) => ({ ...prev, [cacheKey]: result }));
      return result;
    } finally {
      setSimulationLoading(false);
    }
  };

  const fetchFoodbank = () => {
    setFoodbankLoading(true);
    setFoodbankError(null);
    getFoodbankDashboard()
      .then(setFoodbankData)
      .catch(() => setFoodbankError("Failed to load dashboard"))
      .finally(() => setFoodbankLoading(false));
  };

  const analyzeHouseholdGroceries = (
    groceries: string,
    scaleId: string = "100_households",
  ) => {
    setHouseholdLoading(true);
    setHouseholdError(null);
    analyzeHousehold(groceries, scaleId)
      .then(setHouseholdData)
      .catch(() => setHouseholdError("Failed to analyze groceries"))
      .finally(() => setHouseholdLoading(false));
  };

  useEffect(() => {
    // Preload foodbank, household, and all simulated headlines on app load
    let cancelled = false;
    const defaultGroceries =
      "tofu, lentils, dried_beans, oats, bananas, spinach, broccoli, olive_oil, white_rice";
    const defaultScaleId = "100_households";

    // Preload foodbank
    getFoodbankDashboard()
      .then((data) => {
        if (!cancelled) setFoodbankData(data);
      })
      .catch(() => {
        if (!cancelled) setFoodbankError("Failed to load dashboard");
      })
      .finally(() => {
        if (!cancelled) setFoodbankLoading(false);
      });

    setHouseholdLoading(false);

    // Preload simulated headlines sequentially to avoid API rate limits
    const preloadHeadlines = async () => {
      for (const headline of HEADLINES) {
        if (cancelled) break;
        const cacheKey = `${headline.id}:${defaultGroceries}:${defaultScaleId}`;
        try {
          const result = await simulateHeadline(
            defaultGroceries,
            headline.signal,
            defaultScaleId,
          );
          if (!cancelled) {
            setSimulatedResults((prev) => ({ ...prev, [cacheKey]: result }));
          }
        } catch (e) {
          console.error(`Failed to preload headline ${headline.id}:`, e);
        }
      }
    };
    preloadHeadlines();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <DataContext.Provider
      value={{
        foodbankData,
        foodbankLoading,
        foodbankError,
        refetchFoodbank: fetchFoodbank,
        householdData,
        householdLoading,
        householdError,
        analyzeHouseholdGroceries,
        simulatedResults,
        simulateHeadlineWithCache,
        simulationLoading,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useDataContext() {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error("useDataContext must be used within DataProvider");
  }
  return context;
}
