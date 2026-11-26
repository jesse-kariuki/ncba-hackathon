"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowLeft, Check, Globe2, X } from "lucide-react";
import { api, kes, kesFull } from "@/lib/api";
import { ErrorBox, Loading, PageTitle, Severity } from "@/components/ui";

export default function Vendor() {
  const { id } = useParams<{ id: string }>();
  const [v, setV] = useState<any>(null);
  const [err, setErr] = useState("");
  useEffect(() => { api.vendor(id).then(setV).catch((e) => setErr(e.message)); }, [id]);
  if (err) return <ErrorBox msg={err} />;
  if (!v) return <Loading />;
  const c = v.contract;
  const clauses = c ? [["Data protection", c.has_data_protection_clause], ["Exit", c.has_exit_clause], ["Audit rights", c.has_audit_rights_clause]] : [];

  return (
    <div className="space-y-5">
      <Link href="/findings" className="inline-flex items-center gap-1 text-sm text-muted hover:text-brand"><ArrowLeft size={16} /> Findings</Link>
      <PageTitle kicker="Vendor 360" title={v.vendor.vendor_name}
        sub={`${v.vendor.category.replace("_", " ")} · KRA PIN ${v.vendor.kra_pin} · bank ${v.vendor.bank_account} · onboarded ${v.vendor.onboarded_date}`} />
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-4"><div className="text-sm text-muted">Spend, last 12 months</div><div className="text-2xl font-bold">{kes(v.annual_spend_kes)}</div><div className="text-xs text-muted">{v.n_invoices} invoices</div></div>
        <div className="card p-4"><div className="text-sm text-muted">Contract rate</div><div className="text-2xl font-bold">{c ? `${kesFull(c.contract_rate_kes)} / ${c.rate_unit}` : "No contract on file"}</div>
          {c && <div className="text-xs text-muted">{c.auto_renew ? "Auto-renews" : "Expires"} {c.renewal_date} · notice {c.notice_days} days · +{c.annual_escalation_pct}%/yr</div>}</div>
        <div className="card p-4"><div className="text-sm text-muted">Open findings</div><div className="text-2xl font-bold">{v.findings.filter((f: any) => f.status === "open").length}</div></div>
      </div>

      <section className="card p-5">
        <h2 className="font-semibold">Monthly spend {c && <span className="text-sm font-normal text-muted">vs contract rate (dashed)</span>}</h2>
        <div className="mt-4 h-60">
          <ResponsiveContainer>
            <LineChart data={v.monthly_spend} margin={{ right: 20 }}>
              <XAxis dataKey="month" tick={{ fill: "var(--muted)", fontSize: 12 }} />
              <YAxis tickFormatter={(x) => `${(x / 1e3).toFixed(0)}k`} tick={{ fill: "var(--muted)", fontSize: 12 }} width={56} />
              <Tooltip formatter={(x: number) => [kesFull(x), "Billed"]} />
              {c && <ReferenceLine y={c.contract_rate_kes} stroke="var(--rule)" strokeDasharray="6 4" />}
              <Line type="monotone" dataKey="kes" stroke="var(--brand)" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {c && (
        <section className="card p-5">
          <h2 className="font-semibold">Contract check (Data Protection Act 2019 · CBK third-party guidance)</h2>
          <ul className="mt-3 grid gap-2 sm:grid-cols-4">
            {clauses.map(([name, ok]) => (
              <li key={name as string} className={`flex items-center gap-2 rounded-lg p-3 text-sm font-medium ${ok ? "bg-brand/10 text-brand" : "bg-risk/10 text-risk"}`}>
                {ok ? <Check size={16} /> : <X size={16} />} {name as string} clause {ok ? "present" : "missing"}
              </li>
            ))}
            <li className={`flex items-center gap-2 rounded-lg p-3 text-sm font-medium ${c.processes_customer_data && c.data_location !== "KE" ? "bg-risk/10 text-risk" : "bg-brand/10 text-brand"}`}>
              <Globe2 size={16} /> Customer data: {c.processes_customer_data ? (c.data_location === "KE" ? "in Kenya" : `stored in ${c.data_location}`) : "none"}
            </li>
          </ul>
        </section>
      )}

      <section className="card p-5">
        <h2 className="font-semibold">Findings for this vendor</h2>
        <ul className="mt-2 divide-y divide-line">
          {v.findings.map((f: any) => (
            <li key={f.finding_id}><Link href={`/findings/${f.finding_id}`} className="flex items-center gap-3 py-3 hover:text-brand">
              <Severity s={f.severity} /><span className="flex-1">{f.title}</span><b>{f.kes_impact ? kes(f.kes_impact) : "risk"}</b></Link></li>
          ))}
          {v.findings.length === 0 && <li className="py-3 text-muted">No findings. This vendor looks clean.</li>}
        </ul>
      </section>
    </div>
  );
}
