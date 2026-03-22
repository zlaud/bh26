export const SAMPLE_BASKETS = {
  family:
    "eggs, milk, chicken, bread, bananas, apples, pasta, canned_tomatoes, vegetable_oil",
  budget:
    "dried_beans, lentils, white_rice, oats, peanut_butter, potatoes, onions, flour",
  plant:
    "tofu, lentils, dried_beans, oats, bananas, spinach, broccoli, olive_oil, white_rice",
};

export const SCALE_OPTIONS = [
  { id: "100_households", label: "100 households" },
  { id: "1000_households", label: "1,000 households" },
  { id: "campus", label: "Campus (5k people)" },
];

export const RISK_COLORS = {
  HIGH: {
    badge: "bg-red-50 text-red-700 border border-red-200",
    border: "border-red-200",
    bar: "bg-red-500",
    pill: "bg-red-50 border-red-200",
  },
  MEDIUM: {
    badge: "bg-amber-50 text-amber-700 border border-amber-200",
    border: "border-amber-200",
    bar: "bg-amber-500",
    pill: "bg-amber-50 border-amber-200",
  },
  LOW: {
    badge: "bg-green-50 text-green-700 border border-green-200",
    border: "border-green-200",
    bar: "bg-green-500",
    pill: "bg-green-50 border-green-200",
  },
  CRITICAL: {
    badge: "bg-red-100 text-red-800 border border-red-300",
    border: "border-red-300",
    bar: "bg-red-600",
    pill: "bg-red-100 border-red-300",
  },
};

export const URGENCY_COLORS = {
  critical: "text-red-600",
  immediate: "text-amber-600",
  watch: "text-green-600",
};
