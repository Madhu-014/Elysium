"use client";

import { useState } from "react";
import { Check, Clipboard, TerminalSquare } from "lucide-react";

type ApiCodeBlockProps = {
  code: string;
  label: string;
};

export default function ApiCodeBlock({ code, label }: ApiCodeBlockProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-emerald-500/35 bg-black/35 backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-emerald-500/20 bg-black/35 px-4 py-2">
        <div className="flex items-center gap-2 text-xs text-emerald-200">
          <TerminalSquare className="h-4 w-4" />
          {label}
        </div>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 text-xs text-emerald-200 transition hover:bg-emerald-500/20"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Clipboard className="h-3.5 w-3.5" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="overflow-x-auto p-4 text-sm leading-6 text-zinc-100">
        <code>{code}</code>
      </pre>
    </div>
  );
}
