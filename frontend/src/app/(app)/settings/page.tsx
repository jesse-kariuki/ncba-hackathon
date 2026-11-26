"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageTitle } from "@/components/ui";

const RULES = [
  ["Approval limit (split-purchase check)", "KES 1,000,000"],
  ["Duplicate window, same vendor and amount", "45 days"],
  ["Invoice-number similarity for duplicates", "≥ 95%"],
  ["Idle-seat threshold", "> 10% of seats unused for 90 days"],
  ["Renewal alert", "notice deadline within 30 days"],
  ["Overbilling tolerance", "typical month > 112% of contract rate"],
  ["Spend spike", "> 4× the vendor's median month"],
];

export default function Settings() {
  const router = useRouter();
  const [providers, setProviders] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  useEffect(() => { api.health().then((h) => setProviders(h.ai_providers)).catch(() => setProviders(["unreachable"])); }, []);
  return (
    <div className="space-y-6">
      <PageTitle title="Settings" sub="Rules decide. These thresholds are owned by procurement and versioned in the audit trail." />
      <section className="card divide-y divide-line">
        {RULES.map(([k, v]) => <div key={k} className="flex justify-between gap-4 p-4 text-sm"><span>{k}</span><b>{v}</b></div>)}
      </section>
      <section className="card p-5 text-sm">
        <h2 className="font-semibold">AI provider</h2>
        <p className="mt-1">Active: <b>{providers.join(", ") || "…"}</b>. Set <code>GEMINI_API_KEY</code> or <code>ANTHROPIC_API_KEY</code> in <code>.env</code>. Without a key, template explanations are used.</p>
        <p className="mt-1 text-muted">The AI only explains and drafts. It never decides, and personal data is masked before any text is sent.</p>
      </section>
      <section className="card p-5 text-sm">
        <h2 className="font-semibold">Demo</h2>
        <p className="mt-1 text-muted">Clear all decisions and the audit log, and rescan the demo dataset.</p>
        <button disabled={busy} onClick={async () => { setBusy(true); await api.reset(); router.push("/dashboard"); }}
          className="mt-3 rounded-lg border border-risk px-4 py-2 font-semibold text-risk disabled:opacity-40">Reset demo</button>
      </section>
    </div>
  );
}
