"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Download } from "lucide-react";
import { api, ACTIONS, kes, type AuditRow } from "@/lib/api";
import { ErrorBox, Loading, PageTitle, Status } from "@/components/ui";

export default function Audit() {
  const [rows, setRows] = useState<AuditRow[] | null>(null);
  const [err, setErr] = useState("");
  useEffect(() => { api.audit().then(setRows).catch((e) => setErr(e.message)); }, []);
  if (err) return <ErrorBox msg={err} />;
  if (!rows) return <Loading />;

  const exportCsv = () => {
    const head = ["ts", "finding_id", "action", "role", "user", "decision", "comment", "kes_impact"];
    const csv = [head.join(","), ...rows.map((r) => head.map((h) => JSON.stringify((r as any)[h] ?? "")).join(","))].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = "leaklens-audit-log.csv";
    a.click();
  };

  return (
    <div>
      <div className="flex flex-wrap items-start gap-3">
        <div className="flex-1"><PageTitle title="Audit log" sub="Who did what, when. Append-only, ready for internal audit and CBK review." /></div>
        <button onClick={exportCsv} className="inline-flex items-center gap-2 rounded-lg border border-line bg-surface px-3 py-2 text-sm font-medium"><Download size={16} /> Export CSV</button>
      </div>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-muted">
            <tr className="border-b border-line"><th className="p-3">Time</th><th className="p-3">Finding</th><th className="p-3">Action</th><th className="p-3">Role</th><th className="p-3">Decision</th><th className="p-3">Comment</th><th className="p-3 text-right">KES</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-b border-line last:border-0">
                <td className="p-3 whitespace-nowrap">{r.ts.replace("T", " ")}</td>
                <td className="p-3"><Link className="text-brand" href={`/findings/${r.finding_id}`}>{r.finding_id}</Link></td>
                <td className="p-3">{ACTIONS[r.action] ?? r.action}</td><td className="p-3">{r.role}</td>
                <td className="p-3"><Status s={r.decision} /></td><td className="p-3 text-muted">{r.comment || "-"}</td>
                <td className="p-3 text-right">{r.kes_impact ? kes(r.kes_impact) : "-"}</td>
              </tr>
            ))}
            {rows.length === 0 && <tr><td colSpan={7} className="p-6 text-center text-muted">No decisions yet. Approve or reject a finding and it appears here.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
