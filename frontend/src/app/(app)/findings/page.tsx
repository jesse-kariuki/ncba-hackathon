"use client";
import Link from "next/link";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Search } from "lucide-react";
import { api, kes, CAT_ORDER, type Finding, type Summary } from "@/lib/api";
import { ErrorBox, Loading, PageTitle, Severity, Status } from "@/components/ui";

function FindingsInner() {
  const params = useSearchParams();
  const router = useRouter();
  const cat = params.get("category") ?? "all";
  const [F, setF] = useState<Finding[] | null>(null);
  const [s, setS] = useState<Summary | null>(null);
  const [q, setQ] = useState("");
  const [err, setErr] = useState("");
  useEffect(() => { Promise.all([api.findings(), api.summary()]).then(([f, s]) => { setF(f); setS(s); }).catch((e) => setErr(e.message)); }, []);

  const rows = useMemo(() => (F ?? []).filter((f) => (cat === "all" || f.category === cat) &&
    (!q || (f.title + f.vendor_name).toLowerCase().includes(q.toLowerCase()))), [F, cat, q]);

  if (err) return <ErrorBox msg={err} />;
  if (!F || !s) return <Loading />;
  const tabs = [{ key: "all", label: "All", count: F.length }, ...CAT_ORDER.map((k) => {
    const c = s.categories.find((x) => x.key === k)!; return { key: k, label: c.label, count: c.count };
  })];

  return (
    <div>
      <PageTitle title="Findings" sub="Every finding was decided by a rule. Open one to see the evidence, the AI explanation and the action." />
      <div className="flex flex-wrap items-center gap-2">
        {tabs.map((t) => (
          <button key={t.key} onClick={() => router.replace(t.key === "all" ? "/findings" : `/findings?category=${t.key}`)}
            className={`rounded-full border px-3 py-1.5 text-sm ${cat === t.key ? "border-brand bg-brand text-white" : "border-line bg-surface text-muted"}`}>
            {t.label} <span className="opacity-70">({t.count})</span>
          </button>
        ))}
        <label className="ml-auto flex items-center gap-2 rounded-lg border border-line bg-surface px-3 py-1.5">
          <Search size={16} className="text-muted" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search vendor or finding" className="bg-transparent text-sm outline-none" />
        </label>
      </div>
      <div className="card mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-muted">
            <tr className="border-b border-line">
              <th className="p-3">Severity</th><th className="p-3">Finding</th><th className="p-3">Vendor</th>
              <th className="p-3 text-right">KES</th><th className="p-3 text-right">Confidence</th><th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((f) => (
              <tr key={f.finding_id} onClick={() => router.push(`/findings/${f.finding_id}`)}
                className="cursor-pointer border-b border-line last:border-0 hover:bg-bg">
                <td className="p-3"><Severity s={f.severity} /></td>
                <td className="p-3 font-medium"><Link href={`/findings/${f.finding_id}`}>{f.title}</Link></td>
                <td className="p-3 text-muted">{f.vendor_name}</td>
                <td className="p-3 text-right font-semibold whitespace-nowrap">{f.kes_impact ? kes(f.kes_impact) : "risk"}</td>
                <td className="p-3 text-right">{Math.round(f.confidence * 100)}%</td>
                <td className="p-3"><Status s={f.status} /></td>
              </tr>
            ))}
            {rows.length === 0 && <tr><td colSpan={6} className="p-6 text-center text-muted">No findings match.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function Findings() {
  return <Suspense fallback={<Loading />}><FindingsInner /></Suspense>;
}
