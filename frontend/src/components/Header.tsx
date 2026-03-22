"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getPipelineStatus } from "@/lib/api";

export default function Header() {
  const pathname = usePathname();
  const [status, setStatus] = useState<{
    articles: number;
    signals: number;
  } | null>(null);

  useEffect(() => {
    getPipelineStatus()
      .then(setStatus)
      .catch(() => {});
  }, []);

  return (
    <nav className="sticky top-0 z-50 border-b border-stone-200 bg-[var(--bg)]/95 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-8 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[var(--accent)] rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">🌱</span>
          </div>
          <span className="font-serif text-base font-medium text-stone-800">
            Canary<span className="text-[var(--accent)]"></span>
          </span>
        </div>

        <div className="flex gap-1 bg-[var(--bg3)] rounded-xl p-1 border border-stone-200">
          <Link
            href="/household"
            className={`px-4 py-1.5 rounded-lg text-sm transition-all ${
              pathname === "/household"
                ? "bg-white text-[var(--accent)] font-medium shadow-sm"
                : "text-stone-500 hover:text-stone-800"
            }`}
          >
            My Basket
          </Link>
          <Link
            href="/foodbank"
            className={`px-4 py-1.5 rounded-lg text-sm transition-all ${
              pathname === "/foodbank"
                ? "bg-white text-green-700 font-medium shadow-sm"
                : "text-stone-500 hover:text-stone-800"
            }`}
          >
            Food Bank Ops
          </Link>
        </div>

        <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-full px-3 py-1.5">
          <div className="w-1.5 h-1.5 bg-green-600 rounded-full animate-pulse" />
          <span className="font-mono text-xs text-green-700">
            {status ? `live · ${status.signals} signals` : "loading..."}
          </span>
        </div>
      </div>
    </nav>
  );
}
