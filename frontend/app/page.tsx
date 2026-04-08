"use client";

import { useEffect, useMemo, useState } from "react";
import { motion, useScroll, useSpring } from "framer-motion";
import { ArrowRight, BadgeCheck, Code2, Gauge, Github, LineChart, Linkedin, Mail, ShieldCheck, Sparkles } from "lucide-react";
import Link from "next/link";

import ApiCodeBlock from "../components/ApiCodeBlock";
import Playground from "../components/Playground";

type Tab = "python" | "javascript";

const headlineWords = ["Elysium:", "The", "Pure", "State", "of", "Inference"];
const sectionLinks = [
  { href: "#top", label: "Home" },
  { href: "#playground", label: "Playground" },
  { href: "#integration", label: "Integration" },
  { href: "#impact", label: "Impact" },
  { href: "#math", label: "Math" },
];

const fadeUp = {
  initial: { opacity: 0, y: 18 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.25 },
  transition: { duration: 0.55, ease: "easeOut" as const },
};

const cardStagger = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.12,
    },
  },
};

const pythonSnippet = `from openai import OpenAI\n\nclient = OpenAI(\n    api_key="YOUR_KEY",\n    base_url="https://api.elysium.tech/v1"\n)\n\nres = client.responses.create(\n    model="gpt-4o-mini",\n    input="Summarize this architecture doc..."\n)\nprint(res.output_text)`;

const jsSnippet = `import OpenAI from "openai";\n\nconst client = new OpenAI({\n  apiKey: process.env.ELYSIUM_API_KEY,\n  baseURL: "https://api.elysium.tech/v1",\n});\n\nconst res = await client.responses.create({\n  model: "gpt-4o-mini",\n  input: "Summarize this architecture doc...",\n});\n\nconsole.log(res.output_text);`;

function FloatingParticles() {
  const particles = Array.from({ length: 16 }, (_, idx) => idx);

  function particlePosition(id: number) {
    // Deterministic positions prevent SSR/CSR hydration mismatches.
    const x = (id * 37 + 11) % 100;
    const y = (id * 53 + 23) % 100;
    return { x: `${x}%`, y: `${y}%` };
  }

  return (
    <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      {particles.map((id) => {
        const pos = particlePosition(id);
        return (
          <motion.span
            key={id}
            className="absolute h-1.5 w-1.5 rounded-full bg-emerald-300/30"
            initial={{
              x: pos.x,
              y: pos.y,
              opacity: 0.2,
            }}
            animate={{
              y: ["0%", "-30%", "0%"],
              opacity: [0.2, 0.7, 0.2],
            }}
            transition={{
              duration: 8 + (id % 5),
              repeat: Number.POSITIVE_INFINITY,
              ease: "easeInOut",
              delay: id * 0.14,
            }}
          />
        );
      })}
    </div>
  );
}

export default function Page() {
  const [activeTab, setActiveTab] = useState<Tab>("python");
  const { scrollYProgress } = useScroll();
  const progressScaleX = useSpring(scrollYProgress, {
    stiffness: 120,
    damping: 20,
    mass: 0.2,
  });

  const code = useMemo(() => {
    return activeTab === "python" ? pythonSnippet : jsSnippet;
  }, [activeTab]);

  useEffect(() => {
    const navEntry = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
    if (!navEntry || navEntry.type !== "reload") {
      return;
    }

    if (!window.location.hash) {
      return;
    }

    window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}`);
    window.scrollTo({ top: 0, behavior: "auto" });
  }, []);

  return (
    <main id="top" className="relative min-h-screen overflow-x-clip bg-zinc-950 text-zinc-100">
      <motion.div
        style={{ scaleX: progressScaleX }}
        className="fixed left-0 right-0 top-0 z-50 h-1 origin-left bg-gradient-to-r from-emerald-500 via-emerald-300 to-emerald-500"
      />

      <FloatingParticles />
      <div className="pointer-events-none absolute inset-0">
        <div className="grid-atmosphere absolute inset-0 bg-tech-grid opacity-[0.08]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_12%_5%,rgba(16,185,129,0.22),transparent_38%),radial-gradient(circle_at_88%_15%,rgba(6,95,70,0.24),transparent_34%),radial-gradient(circle_at_50%_120%,rgba(16,185,129,0.08),transparent_40%)]" />
        <div className="aurora-orb absolute -right-20 top-24 h-72 w-72 rounded-full bg-emerald-500/20 blur-3xl" />
        <div className="aurora-orb-reverse absolute -left-20 bottom-24 h-72 w-72 rounded-full bg-emerald-800/20 blur-3xl" />
      </div>

      <header className="sticky top-3 z-40 mx-auto w-full max-w-6xl px-6">
        <motion.nav
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: "easeOut" }}
          className="glass-panel flex items-center justify-between rounded-2xl px-4 py-3 sm:px-5"
        >
          <Link
            href="#top"
            className="px-2 text-sm font-semibold uppercase tracking-[0.16em] text-emerald-300 transition-colors duration-300 hover:text-emerald-200"
          >
            Elysium
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            {sectionLinks.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-lg px-3 py-2 text-xs font-medium text-zinc-200 transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-500/10 hover:text-emerald-200 sm:text-sm"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </motion.nav>
      </header>

      <section className="relative mx-auto max-w-6xl px-6 pb-10 pt-12 sm:pt-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="inline-flex items-center gap-2 rounded-full border border-emerald-500/25 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300 backdrop-blur"
        >
          <Sparkles className="h-3.5 w-3.5" />
          Elysium Sustainability Engine
        </motion.div>

        <motion.h1
          initial="hidden"
          animate="visible"
          whileHover={{ textShadow: "0 0 24px rgba(16,185,129,0.35)" }}
          variants={{
            visible: { transition: { staggerChildren: 0.07 } },
            hidden: {},
          }}
          className="mt-6 max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-6xl"
        >
          {headlineWords.map((word) => (
            <motion.span
              key={word}
              variants={{
                hidden: { opacity: 0, y: 16 },
                visible: { opacity: 1, y: 0 },
              }}
              transition={{ duration: 0.45, ease: "easeOut" }}
              className="mr-3 inline-block"
            >
              {word}
            </motion.span>
          ))}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.1, ease: "easeOut" }}
          className="mt-6 max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg"
        >
          A high-performance Green AI middleware that purifies noisy prompts,
          preserves semantic integrity, and compounds long-term sustainability wins.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }}
          className="mt-10 flex flex-col gap-3 sm:flex-row"
        >
          <Link
            href="#playground"
            className="inline-flex items-center justify-center rounded-lg bg-emerald-500 px-5 py-3 text-sm font-medium text-zinc-950 shadow-glow transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-400"
          >
            Try the API (Free)
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
          <Link
            href="#math"
            className="inline-flex items-center justify-center rounded-lg border border-zinc-700 bg-zinc-900 px-5 py-3 text-sm font-medium text-zinc-100 transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:text-emerald-200"
          >
            View the Math
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.22, ease: "easeOut" }}
          className="mt-8 inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-zinc-300"
        >
          <BadgeCheck className="h-3.5 w-3.5 text-emerald-300" />
          Trusted by frontier teams to scale efficient, carbon-aware inference.
        </motion.div>
      </section>

      <section id="mission" className="relative mx-auto mt-10 max-w-6xl px-6">
        <motion.div
          variants={cardStagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.25 }}
          className="grid gap-4 md:grid-cols-3"
        >
          <motion.article
            variants={fadeUp}
            whileHover={{ y: -6, rotate: -0.4 }}
            className="relative overflow-hidden rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-emerald-500/15 via-zinc-950 to-zinc-900 p-5 shadow-[0_0_24px_rgba(16,185,129,0.14)]"
          >
            <motion.div
              animate={{ x: ["-120%", "220%"] }}
              transition={{ repeat: Number.POSITIVE_INFINITY, duration: 3.8, ease: "easeInOut" }}
              className="pointer-events-none absolute inset-y-0 w-20 bg-gradient-to-r from-transparent via-emerald-200/20 to-transparent blur-sm"
            />
            <div className="relative z-10">
              <p className="text-xs uppercase tracking-[0.18em] text-emerald-300/90">Signal Pruning</p>
              <p className="mt-3 text-sm leading-6 text-zinc-200">
                Elysium removes repetitive prompt noise before inference, preventing wasteful
                GPU cycles without stripping core intent.
              </p>
            </div>
          </motion.article>

          <motion.article
            variants={fadeUp}
            whileHover={{ y: -6, scale: 1.01 }}
            className="rounded-2xl border border-white/10 bg-zinc-900/50 p-5"
          >
            <div className="flex items-center gap-2 text-emerald-300">
              <ShieldCheck className="h-4 w-4" />
              <p className="text-xs uppercase tracking-[0.18em]">Protocol Layer</p>
            </div>
            <div className="mt-4 space-y-3 border-l border-emerald-500/25 pl-4 text-xs text-zinc-300">
              <p><span className="text-emerald-300">1.</span> Token accounting and deduplication</p>
              <p><span className="text-emerald-300">2.</span> Relevance shaping with context guardrails</p>
              <p><span className="text-emerald-300">3.</span> Context-safe compression by mode</p>
            </div>
          </motion.article>

          <motion.article
            variants={fadeUp}
            whileHover={{ y: -6, rotate: 0.4 }}
            className="rounded-2xl border border-white/10 bg-black/35 p-5"
          >
            <div className="mb-4 flex items-center gap-2 text-emerald-300">
              <Gauge className="h-4 w-4" />
              <p className="text-xs uppercase tracking-[0.18em]">Impact Ledger</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded-lg border border-white/10 bg-zinc-900/70 p-2">
                <p className="text-[10px] text-zinc-500">Latency Drift</p>
                <p className="mt-1 text-sm font-semibold text-white">-18%</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-zinc-900/70 p-2">
                <p className="text-[10px] text-zinc-500">Token Waste</p>
                <p className="mt-1 text-sm font-semibold text-white">-42%</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-zinc-900/70 p-2">
                <p className="text-[10px] text-zinc-500">Energy / req</p>
                <p className="mt-1 text-sm font-semibold text-white">-0.31 mWh</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-zinc-900/70 p-2">
                <p className="text-[10px] text-zinc-500">CO2 / req</p>
                <p className="mt-1 text-sm font-semibold text-white">-1.2 mg</p>
              </div>
            </div>
          </motion.article>
        </motion.div>
      </section>

      <section className="relative mx-auto mt-12 max-w-6xl px-6">
        <motion.div {...fadeUp} className="glass-panel rounded-2xl p-6">
          <p className="text-xs uppercase tracking-[0.18em] text-emerald-300/80">Why Elysium Over Others</p>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <motion.article
              whileHover={{ y: -6, scale: 1.01 }}
              className="rounded-xl border border-white/10 bg-black/30 p-4 transition-all duration-300 hover:border-emerald-500/30 hover:shadow-[0_0_20px_rgba(16,185,129,0.12)]"
            >
              <p className="text-sm font-semibold text-white">Optimization + Integrity Together</p>
              <p className="mt-2 text-xs leading-5 text-zinc-400">
                Most gateways optimize for raw compression only. Elysium optimizes while
                exposing semantic integrity, so teams can reduce tokens without hidden quality loss.
              </p>
            </motion.article>
            <motion.article
              whileHover={{ y: -6, rotate: -0.5 }}
              className="rounded-xl border border-white/10 bg-black/30 p-4 transition-all duration-300 hover:border-emerald-500/30 hover:shadow-[0_0_20px_rgba(16,185,129,0.12)]"
            >
              <p className="text-sm font-semibold text-white">Transparent Climate Math</p>
              <p className="mt-2 text-xs leading-5 text-zinc-400">
                Elysium returns token deltas, energy, and CO2 estimates per request with explicit
                assumptions, making sustainability claims auditable and credible.
              </p>
            </motion.article>
            <motion.article
              whileHover={{ y: -6, rotate: 0.5 }}
              className="rounded-xl border border-white/10 bg-black/30 p-4 transition-all duration-300 hover:border-emerald-500/30 hover:shadow-[0_0_20px_rgba(16,185,129,0.12)]"
            >
              <p className="text-sm font-semibold text-white">Middleware-First for Fast Adoption</p>
              <p className="mt-2 text-xs leading-5 text-zinc-400">
                Teams integrate with a one-line base URL swap instead of rewriting app logic,
                which accelerates rollout across every model provider and product surface.
              </p>
            </motion.article>
          </div>
        </motion.div>
      </section>

      <Playground />

      <section id="integration" className="relative mx-auto mt-24 max-w-6xl px-6">
        <motion.div {...fadeUp} className="mb-6 flex items-center gap-2 text-sm text-emerald-300/80">
          <Code2 className="h-4 w-4" />
          Integration in One Line
        </motion.div>

        <div className="glow-shell overflow-hidden rounded-2xl border border-white/10 bg-zinc-950/90">
          <div className="flex items-center gap-2 border-b border-white/10 p-2">
            <button
              type="button"
              onClick={() => setActiveTab("python")}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                activeTab === "python"
                  ? "bg-emerald-500/20 text-emerald-300"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Python
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("javascript")}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                activeTab === "javascript"
                  ? "bg-emerald-500/20 text-emerald-300"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              JavaScript
            </button>
          </div>

          <div className="border-b border-emerald-500/20 bg-emerald-500/8 px-4 py-2 text-xs text-emerald-200">
            One-line swap: <span className="font-mono">base_url=&quot;https://api.elysium.tech/v1&quot;</span>
          </div>

          <div className="p-4">
            <ApiCodeBlock code={code} label="Elysium Integration" />
          </div>
        </div>
      </section>

      <section id="impact" className="relative mx-auto mb-24 mt-24 max-w-6xl px-6">
        <motion.div {...fadeUp} className="mb-6 flex items-center gap-2 text-sm text-emerald-300/80">
          <LineChart className="h-4 w-4" />
          Impact Dashboard
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-zinc-900 via-zinc-950 to-black p-8 shadow-[0_0_56px_rgba(16,185,129,0.18)]"
        >
          <div id="math" className="mb-5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-xs text-emerald-200">
            Estimation model: energy saved (kWh) = (tokens saved / 1000) x kWh per 1k tokens,
            and CO2 saved (g) = energy saved x grid carbon intensity.
          </div>
          <div className="mb-5 rounded-xl border border-white/10 bg-black/30 p-4 text-xs text-zinc-300">
            Long-run view: if a platform processes 100M requests/day and Elysium removes even 15%
            token overhead, yearly avoided compute and emissions become material at infrastructure scale.
          </div>
          <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">Global Live Impact</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-black/40 p-4">
              <p className="text-2xl font-semibold text-white">14.2M</p>
              <p className="mt-1 text-xs text-zinc-400">Tokens Saved</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/40 p-4">
              <p className="text-2xl font-semibold text-white">4.2 Tons</p>
              <p className="mt-1 text-xs text-zinc-400">CO2 Prevented</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/40 p-4">
              <p className="text-2xl font-semibold text-white">1,200</p>
              <p className="mt-1 text-xs text-zinc-400">Trees Equivalent</p>
            </div>
          </div>
        </motion.div>
      </section>

      <section className="relative mx-auto mt-20 max-w-6xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.55, ease: "easeOut" }}
          className="glass-panel overflow-hidden rounded-2xl p-6"
        >
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-emerald-500/20 to-transparent blur-2xl" />
            <p className="text-xs uppercase tracking-[0.18em] text-emerald-300/80">Build Sustainable AI At Scale</p>
            <h3 className="mt-2 max-w-2xl text-2xl font-semibold text-white">
              Elysium turns every prompt into an efficiency decision that compounds into measurable climate and cost outcomes.
            </h3>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href="#playground"
                className="inline-flex items-center rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-zinc-950 transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-400"
              >
                Launch Live Optimization
              </Link>
              <Link
                href="#impact"
                className="inline-flex items-center rounded-lg border border-emerald-500/30 bg-black/30 px-4 py-2 text-sm text-emerald-200 transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-500/10"
              >
                Explore Impact Model
              </Link>
              <Link
                href="#top"
                className="inline-flex items-center rounded-lg border border-white/15 bg-black/30 px-4 py-2 text-sm text-zinc-200 transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-500/30"
              >
                Back to Top
              </Link>
            </div>
          </div>
        </motion.div>
      </section>

      <footer className="relative mx-auto mb-10 mt-8 max-w-6xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="glass-panel rounded-2xl px-5 py-5 text-sm text-zinc-300"
        >
          <div className="grid gap-5 md:grid-cols-3">
            <div>
              <p className="text-xs uppercase tracking-[0.15em] text-emerald-300/80">Developed By</p>
              <p className="mt-2 text-base font-semibold text-white">Madhusudhan Chandar</p>
              <p className="mt-1 text-xs text-zinc-400">Creative technologist building sustainable AI systems.</p>
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.15em] text-emerald-300/80">Connect</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <a
                  href="https://github.com/Madhu-014"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:text-emerald-300"
                >
                  <Github className="h-3.5 w-3.5" /> GitHub
                </a>
                <a
                  href="https://www.linkedin.com/in/madhusudhan-chandar-581b49309/"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:text-emerald-300"
                >
                  <Linkedin className="h-3.5 w-3.5" /> LinkedIn
                </a>
              </div>
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.15em] text-emerald-300/80">Contact</p>
              <a
                href="mailto:madhusudhanchandar@gmail.com"
                className="mt-3 inline-flex items-center gap-2 rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:text-emerald-300"
              >
                <Mail className="h-3.5 w-3.5" /> madhusudhanchandar@gmail.com
              </a>
            </div>
          </div>

          <div className="mt-5 border-t border-white/10 pt-3 text-xs text-zinc-500">
            © 2026 Elysium. Engineered for high-integrity, low-carbon inference.
          </div>
        </motion.div>
      </footer>
    </main>
  );
}
