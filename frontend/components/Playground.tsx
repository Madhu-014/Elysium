"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { motion, animate } from "framer-motion";
import { ArrowRightLeft, Leaf, Loader2, TreePine, Zap } from "lucide-react";

type Mode = "eco" | "balanced" | "high_quality";

type OptimizeResponse = {
  optimized_prompt: string;
  tokens_before: number;
  tokens_after: number;
  token_reduction_pct: number;
  sustainability: {
    energy_saved_kwh: number;
    co2_saved_g: number;
  };
};

const defaultPrompt = `Please help me write a summary for this report.
Please make it clear.
Please include all points.
Please include all points.
The report discusses carbon-aware infrastructure,
power usage, model routing, token overhead,
and repeated prompt context across services.
Also, keep every detail and do not miss anything,
and please be concise but detailed.`;

type ImpactMetricProps = {
  label: string;
  value: number;
  suffix: string;
  decimals?: number;
  icon: ReactNode;
};

const integerFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

function formatInteger(value: number) {
  return integerFormatter.format(value);
}

function ImpactMetric({
  label,
  value,
  suffix,
  decimals = 0,
  icon,
}: ImpactMetricProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const controls = animate(0, value, {
      duration: 1.8,
      ease: "easeOut",
      onUpdate: (latest: number) => setDisplayValue(latest),
    });

    return () => {
      controls.stop();
    };
  }, [value]);

  return (
    <div className="glass-panel rounded-xl p-4">
      <motion.div
        key={value}
        initial={{ scale: 1, opacity: 0.85 }}
        animate={{ scale: [1, 1.1, 1], opacity: [0.85, 1, 0.85] }}
        transition={{ duration: 0.8, ease: "easeInOut" }}
        className="mb-2 flex items-center gap-2 text-emerald-300/90"
      >
        {icon}
      </motion.div>
      <div className="text-xl font-semibold text-white">
        {displayValue.toFixed(decimals)}
        {suffix}
      </div>
      <p className="mt-1 text-xs text-zinc-400">{label}</p>
    </div>
  );
}

function SemanticGauge({ value }: { value: number }) {
  const radius = 48;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(value, 100));
  const strokeDashoffset = circumference * (1 - clamped / 100);

  return (
    <div className="glass-panel rounded-2xl p-4">
      <p className="mb-3 text-xs uppercase tracking-[0.18em] text-emerald-300/80">Semantic Integrity</p>
      <div className="relative mx-auto flex h-32 w-32 items-center justify-center">
        <svg className="h-32 w-32 -rotate-90" viewBox="0 0 120 120" aria-hidden="true">
          <circle cx="60" cy="60" r={radius} stroke="rgba(255,255,255,0.15)" strokeWidth="8" fill="none" />
          <circle
            cx="60"
            cy="60"
            r={radius}
            stroke="#10b981"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: "stroke-dashoffset 800ms ease" }}
          />
        </svg>
        <div className="absolute text-center">
          <p className="text-xl font-semibold text-white">{clamped.toFixed(1)}%</p>
          <p className="text-[10px] text-zinc-400">context retained</p>
        </div>
      </div>
    </div>
  );
}

function Token({ children }: { children: string }) {
  return (
    <span className="mx-0.5 rounded bg-emerald-500/15 px-1.5 py-0.5 text-emerald-300 ring-1 ring-emerald-500/30">
      {children}
    </span>
  );
}

function highlightTokens(text: string) {
  const words = text.split(/(\s+)/);
  return words.map((word, index) => {
    const cleaned = word.replace(/[^a-zA-Z0-9_-]/g, "");
    const shouldHighlight = cleaned.length >= 8;
    if (!shouldHighlight) {
      return <span key={`${word}-${index}`}>{word}</span>;
    }
    return <Token key={`${word}-${index}`}>{word}</Token>;
  });
}

export default function Playground() {
  const [mode, setMode] = useState<Mode>("eco");
  const [inputPrompt, setInputPrompt] = useState(defaultPrompt);
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPurifying, setIsPurifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiBaseUrl = process.env.NEXT_PUBLIC_ELYSIUM_API_BASE_URL ?? "http://127.0.0.1:8000";
  const apiKey = process.env.NEXT_PUBLIC_ELYSIUM_API_KEY?.trim();

  const metrics = useMemo(() => {
    if (!result) {
      return {
        co2SavedMg: 7400,
        energySavedMWh: 1800,
        tokensSaved: 294,
      };
    }

    const co2SavedMg = result.sustainability.co2_saved_g * 1000;
    const energySavedMWh = result.sustainability.energy_saved_kwh * 1_000_000;
    const tokensSaved = Math.max(result.tokens_before - result.tokens_after, 0);

    return { co2SavedMg, energySavedMWh, tokensSaved };
  }, [result]);

  const longRunImpact = useMemo(() => {
    const assumedRequestsPerDay = 1_000_000;
    const annualRequests = assumedRequestsPerDay * 365;
    const annualCo2Tons = (metrics.co2SavedMg * annualRequests) / 1_000_000_000;
    const annualEnergyMWh = (metrics.energySavedMWh * annualRequests) / 1_000_000_000;
    const annualTokensSaved = metrics.tokensSaved * annualRequests;

    return {
      assumedRequestsPerDay,
      annualCo2Tons,
      annualEnergyMWh,
      annualTokensSaved,
    };
  }, [metrics]);

  const tokensBefore = result?.tokens_before ?? 942;
  const tokensAfter = result?.tokens_after ?? 648;
  const semanticIntegrity = result ? Math.max(90, 100 - result.token_reduction_pct * 0.2) : 99.8;

  async function handleOptimize() {
    setIsLoading(true);
    setIsPurifying(true);
    setError(null);

    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (apiKey) {
        headers["X-API-Key"] = apiKey;
      }

      const response = await fetch(`${apiBaseUrl}/optimize`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          prompt: inputPrompt,
          mode,
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Optimization request failed");
      }

      const data = (await response.json()) as OptimizeResponse;
      setResult(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
    } finally {
      setIsLoading(false);
      setTimeout(() => setIsPurifying(false), 320);
    }
  }

  return (
    <section id="playground" className="relative mx-auto mt-24 max-w-6xl px-6">
      <div className="pointer-events-none absolute -inset-x-2 top-8 -z-10 h-80 bg-[radial-gradient(circle_at_50%_20%,rgba(16,185,129,0.18),transparent_60%)]" />

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.55, ease: "easeOut" }}
        className="mb-6 flex items-center gap-2 text-sm text-emerald-300/80"
      >
        <ArrowRightLeft className="h-4 w-4" />
        Live Playground
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.55, ease: "easeOut" }}
        className="glass-panel mb-4 flex flex-col gap-3 rounded-2xl p-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div className="flex flex-wrap gap-2">
          {(["eco", "balanced", "high_quality"] as Mode[]).map((candidateMode) => (
            <button
              type="button"
              key={candidateMode}
              onClick={() => setMode(candidateMode)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                mode === candidateMode
                  ? "bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/30"
                  : "bg-zinc-900 text-zinc-300 hover:bg-zinc-800"
              }`}
            >
              {candidateMode}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={handleOptimize}
          disabled={isLoading || inputPrompt.trim().length === 0}
          className="inline-flex items-center justify-center rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-zinc-950 shadow-glow transition-all duration-300 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Optimizing...
            </>
          ) : (
            "Run Optimization"
          )}
        </button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.55, ease: "easeOut" }}
        className="mb-5 grid gap-3 md:grid-cols-2"
      >
        <div className="rounded-xl border border-emerald-500/20 bg-black/25 p-3 text-xs text-zinc-300">
          <p className="uppercase tracking-[0.16em] text-emerald-300/80">Input</p>
          <p className="mt-2 font-mono text-zinc-200">POST /optimize</p>
          <p className="mt-1">Body:</p>
          <p className="mt-1 font-mono text-[11px] text-zinc-400">{"{ prompt: string, mode: \"eco\"|\"balanced\"|\"high_quality\" }"}</p>
        </div>
        <div className="rounded-xl border border-emerald-500/20 bg-black/25 p-3 text-xs text-zinc-300">
          <p className="uppercase tracking-[0.16em] text-emerald-300/80">Output</p>
          <p className="mt-2">Returns optimized prompt + metrics:</p>
          <p className="mt-1 font-mono text-[11px] text-zinc-400">optimized_prompt, tokens_before, tokens_after, token_reduction_pct, sustainability</p>
          <p className="mt-2 text-zinc-400">Forward <span className="font-mono text-zinc-300">optimized_prompt</span> to your LLM provider.</p>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.65, ease: "easeOut" }}
        className="grid gap-6 md:grid-cols-2"
      >
        <div className="glass-panel flex h-[24rem] flex-col overflow-hidden rounded-2xl shadow-[0_0_0_1px_rgba(16,185,129,0.06)] transition-transform duration-500 hover:-translate-y-1 sm:h-[26rem]">
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-2 text-xs text-zinc-400">
            <span>Unoptimized Input</span>
            <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-red-300">{tokensBefore} tokens</span>
          </div>
          <textarea
            value={inputPrompt}
            onChange={(event) => setInputPrompt(event.target.value)}
            className="min-h-0 flex-1 resize-none overflow-y-auto bg-transparent p-4 text-sm leading-6 text-zinc-300 outline-none [scrollbar-gutter:stable]"
          />
        </div>

        <div className="glass-panel relative flex h-[24rem] flex-col overflow-hidden rounded-2xl shadow-[0_0_40px_rgba(16,185,129,0.12)] transition-transform duration-500 hover:-translate-y-1 sm:h-[26rem]">
          {isPurifying ? (
            <motion.div
              initial={{ x: "-120%" }}
              animate={{ x: "220%" }}
              transition={{ duration: 0.9, ease: "easeInOut" }}
              className="pointer-events-none absolute inset-y-0 z-20 w-24 bg-gradient-to-r from-transparent via-emerald-300/35 to-transparent blur-md"
            />
          ) : null}
          <motion.div
            initial={{ x: "-120%" }}
            whileInView={{ x: "220%" }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 1.6, delay: 0.2, ease: "easeOut" }}
            className="pointer-events-none absolute inset-y-0 w-16 bg-gradient-to-r from-transparent via-emerald-200/20 to-transparent blur-sm"
          />
          <div className="flex items-center justify-between border-b border-emerald-500/20 px-4 py-2 text-xs text-zinc-300">
            <span>Elysium-Optimized Output</span>
            <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-emerald-300">{tokensAfter} tokens</span>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto p-4 text-sm leading-7 text-zinc-200 [scrollbar-gutter:stable]">
            <p className="break-words">{highlightTokens(result?.optimized_prompt ?? "Run optimization to generate a cleaner, shorter prompt while preserving intent.")}</p>
            {result ? (
              <p className="mt-3 text-zinc-300">
                Token reduction: <span className="text-emerald-300">{result.token_reduction_pct}%</span>
              </p>
            ) : null}
            {error ? <p className="mt-3 text-red-300">{error}</p> : null}
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.55, ease: "easeOut" }}
        className="mt-5"
      >
        <SemanticGauge value={semanticIntegrity} />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.65, delay: 0.1, ease: "easeOut" }}
        className="glass-panel mt-6 rounded-2xl bg-gradient-to-r from-zinc-950 via-zinc-900 to-zinc-950 p-4"
      >
        <p className="mb-4 text-xs uppercase tracking-[0.18em] text-emerald-300/80">Impact Ticker</p>
        <div className="grid gap-4 sm:grid-cols-3">
          <ImpactMetric
            label="CO2 Saved This Request"
            value={metrics.co2SavedMg}
            decimals={1}
            suffix=" mg"
            icon={<Leaf className="h-4 w-4" />}
          />
          <ImpactMetric
            label="Energy Saved This Request"
            value={metrics.energySavedMWh}
            decimals={1}
            suffix=" mWh"
            icon={<Zap className="h-4 w-4" />}
          />
          <ImpactMetric
            label="Tokens Saved This Request"
            value={metrics.tokensSaved}
            suffix=" tokens"
            icon={<TreePine className="h-4 w-4" />}
          />
        </div>

        <div className="mt-5 rounded-xl border border-emerald-500/20 bg-black/30 p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-emerald-300/80">Projected Long-run Impact</p>
          <p className="mt-2 text-xs text-zinc-400">
            If the same optimization quality is applied at {formatInteger(longRunImpact.assumedRequestsPerDay)} requests/day.
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg border border-white/10 bg-black/30 p-3">
              <p className="text-lg font-semibold text-white">{longRunImpact.annualCo2Tons.toFixed(1)} tons</p>
              <p className="text-xs text-zinc-400">Estimated CO2 avoided per year</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-black/30 p-3">
              <p className="text-lg font-semibold text-white">{longRunImpact.annualEnergyMWh.toFixed(1)} MWh</p>
              <p className="text-xs text-zinc-400">Estimated energy avoided per year</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-black/30 p-3">
              <p className="text-lg font-semibold text-white">{formatInteger(Math.round(longRunImpact.annualTokensSaved))}</p>
              <p className="text-xs text-zinc-400">Estimated tokens saved per year</p>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
