"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowRight, Copy, Layers, FileWarning, Activity, ShieldAlert } from "lucide-react";
import { api, ACTIONS, kes, type Summary } from "@/lib/api";
import { ErrorBox, Loading } from "@/components/ui";

const ICONS: Record<string, any> = { duplicates: Copy, overlap: Layers, contracts: FileWarning, anomalies: Activity, risk: ShieldAlert };

export default function Dashboard() {
  const [s, setS] = useState<Summary | null>(null);
  const [err, setErr] = useState("");
  useEffect(() => { api.summary().then(setS).catch((e) => setErr(e.message)); }, []);
  if (err) return <ErrorBox msg={err} />;
  if (!s) return <Loading />;

  const chart = s.categories.filter((c) => c.kes > 0).map((c) => ({ name: c.label, m: +(c.kes / 1e6).toFixed(1) }));
  return (
    <div className="space-y-6">
      <section className="card p-6 md:p-8">
        <p className="text-sm font-semibold uppercase tracking-wider text-brand">Reduce</p>
        <div className="mt-1 text-5xl font-extrabold tracking-tight text-brand md:text-7xl">{kes(s.total_kes)}</div>
        <p className="mt-2 text-lg">avoidable spend found</p>
        <p className="text-sm text-muted">
          {s.n_findings} findings · {s.scan.n_invoices.toLocaleString()} invoices from {s.scan.n_vendors} vendors scanned in {s.scan.seconds}s · {s.scan.source === "upload" ? "your uploaded data" : "illustrative demo data"}
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {s.categories.map((c) => {
          const Icon = ICONS[c.key];
          return (
            <Link key={c.key} href={`/findings?category=${c.key}`} className="card p-4 transition hover:border-brand">
              <Icon size={20} className={c.key === "risk" ? "text-risk" : "text-brand"} />
              <div className="mt-2 text-sm font-semibold leading-tight">{c.label}</div>
              <div className="mt-2 text-2xl font-bold">{c.key === "risk" ? `${c.count} vendors` : kes(c.kes)}</div>
              <div className="text-xs text-muted">{c.count} findings · {c.high} high</div>
            </Link>
          );
        })}
      </section>

      <div className="grid gap-6 lg:grid-cols-5">
        <section className="card p-5 lg:col-span-3">
          <h2 className="font-semibold">Avoidable spend by category (KES millions)</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer>
              <BarChart data={chart} layout="vertical" margin={{ left: 20, right: 20 }}>
                <XAxis type="number" tick={{ fill: "var(--muted)", fontSize: 12 }} />
                <YAxis type="category" dataKey="name" width={170} tick={{ fill: "var(--ink)", fontSize: 12 }} />
                <Tooltip formatter={(v: number) => [`KES ${v}m`, "Avoidable"]} cursor={{ fill: "var(--line)" }} />
                <Bar dataKey="m" fill="var(--brand)" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="card p-5 lg:col-span-2">
          <h2 className="font-semibold">Top 5 actions this week</h2>
          <ul className="mt-3 divide-y divide-line">
            {s.top_actions.map((a) => (
              <li key={a.finding_id}>
                <Link href={`/findings/${a.finding_id}`} className="flex items-center gap-3 py-3 hover:text-brand">
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium">{a.title}</div>
                    <div className="truncate text-xs text-muted">{a.vendor_name} · {ACTIONS[a.suggested_action]}</div>
                  </div>
                  <div className="text-sm font-bold">{a.kes_impact ? kes(a.kes_impact) : "risk"}</div>
                  <ArrowRight size={16} />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-4">
        {(["reuse", "automate", "reduce", "eliminate"] as const).map((k) => (
          <div key={k} className="bg-surface p-4">
            <div className="text-xs font-bold uppercase tracking-wider text-brand">{k}</div>
            <div className="mt-1 text-sm">{s.theme[k]}</div>
          </div>
        ))}
      </section>
    </div>
  );
}
