"use client";
import { useEffect, useState } from "react";
import { api, kes, type AuditRow, type Summary } from "@/lib/api";
import { ErrorBox, Loading, PageTitle } from "@/components/ui";

export default function Savings() {
  const [s, setS] = useState<Summary | null>(null);
  const [a, setA] = useState<AuditRow[]>([]);
  const [err, setErr] = useState("");
  useEffect(() => { Promise.all([api.summary(), api.audit()]).then(([s, a]) => { setS(s); setA(a); }).catch((e) => setErr(e.message)); }, []);
  if (err) return <ErrorBox msg={err} />;
  if (!s) return <Loading />;
  const found = s.savings.found_kes, approved = s.savings.approved_kes;
  const pct = found ? Math.round((approved / found) * 100) : 0;
  const caught = a.filter((r) => r.decision === "approved" && ["hold_payment", "request_credit_note"].includes(r.action));

  return (
    <div className="space-y-6">
      <PageTitle kicker="Eliminate" title="Savings tracker" sub="From finding, to approved action, to money back. Every step has an owner." />
      <section className="card p-6">
        {[["Found by the rules", found, 100, "bg-gold"], ["Approved by a manager", approved, pct, "bg-brand"]].map(([label, val, w, cls]) => (
          <div key={label as string} className="mb-5 last:mb-0">
            <div className="flex justify-between text-sm"><span className="font-medium">{label as string}</span><b>{kes(val as number)}</b></div>
            <div className="mt-2 h-4 rounded-full bg-line"><div className={`h-4 rounded-full ${cls}`} style={{ width: `${Math.max(w as number, 2)}%` }} /></div>
          </div>
        ))}
        <p className="mt-4 text-sm text-muted">Recovered amounts are confirmed once vendors issue credit notes or seats are cancelled at renewal. In a pilot they come from the AP ledger.</p>
      </section>
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card p-5"><div className="text-sm text-muted">Approved actions</div><div className="text-3xl font-bold">{s.savings.approved_count}</div></div>
        <div className="card p-5"><div className="text-sm text-muted">Still open</div><div className="text-3xl font-bold">{s.savings.open_count}</div></div>
        <div className="card p-5"><div className="text-sm text-muted">Duplicate payments stopped before payment</div><div className="text-3xl font-bold">{caught.length}</div></div>
      </div>
      <section className="card p-5">
        <h2 className="font-semibold">Before vs after LeakLens</h2>
        <div className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
          <div className="rounded-xl bg-bg p-4"><b>Before</b><ul className="mt-2 list-disc space-y-1 pl-5 text-muted">
            <li>Duplicates found in the annual audit, after the money left</li><li>Licences renewed at full seat count</li><li>Renewal notice deadlines missed</li><li>Vendor clauses checked by hand, if at all</li></ul></div>
          <div className="rounded-xl bg-brand/10 p-4"><b>After</b><ul className="mt-2 list-disc space-y-1 pl-5">
            <li>Duplicates flagged before payment, with the eTIMS match as proof</li><li>Idle seats cancelled at renewal</li><li>Notice deadlines surfaced 30 days ahead</li><li>Every contract checked against the DPA and CBK guidance</li></ul></div>
        </div>
      </section>
    </div>
  );
}
