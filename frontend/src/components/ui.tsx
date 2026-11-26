"use client";
import { AlertTriangle, CircleDot, Info } from "lucide-react";

export function Severity({ s }: { s: "high" | "medium" | "low" }) {
  const m = { high: ["bg-risk/10 text-risk", AlertTriangle, "High"], medium: ["bg-gold/15 text-ink", CircleDot, "Medium"], low: ["bg-line text-muted", Info, "Low"] } as const;
  const [cls, Icon, label] = m[s];
  return <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${cls}`}><Icon size={12} />{label}</span>;
}

export function Status({ s }: { s: string }) {
  const cls = s === "approved" ? "bg-brand/10 text-brand" : s === "rejected" ? "bg-line text-muted" : "bg-gold/15 text-ink";
  return <span className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${cls}`}>{s}</span>;
}

export function Loading() {
  return <div className="animate-pulse space-y-4"><div className="h-28 rounded-2xl bg-line/60" /><div className="h-64 rounded-2xl bg-line/60" /></div>;
}

export function ErrorBox({ msg }: { msg: string }) {
  return (
    <div className="card border-risk/40 p-5 text-risk">
      Couldn&apos;t reach the LeakLens API ({msg}). Start it with <code className="rounded bg-bg px-1">uvicorn backend.main:app --port 8000</code> from the repo root.
    </div>
  );
}

export function PageTitle({ kicker, title, sub }: { kicker?: string; title: string; sub?: string }) {
  return (
    <div className="mb-6">
      {kicker && <p className="text-sm font-semibold uppercase tracking-wider text-brand">{kicker}</p>}
      <h1 className="text-2xl font-bold md:text-3xl">{title}</h1>
      {sub && <p className="mt-1 text-muted">{sub}</p>}
    </div>
  );
}
