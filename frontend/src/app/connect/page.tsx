"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, Database, FileText, KeyRound, Receipt, Upload } from "lucide-react";
import { Logo } from "@/components/Logo";
import { uploadStore } from "@/lib/api";

const SOURCES = [
  { icon: Database, name: "ERP / Accounts-payable export", detail: "2,988 invoices · 251 vendors · 12 months" },
  { icon: Receipt, name: "KRA eTIMS invoice numbers", detail: "Matched on every invoice" },
  { icon: FileText, name: "Contract repository", detail: "23 contracts · terms and clauses extracted" },
  { icon: KeyRound, name: "Licence admin reports", detail: "Microsoft 365, Adobe, Salesforce + 4 more" },
];
const SLOTS = [
  { key: "vendors", label: "vendors.csv", required: true },
  { key: "invoices", label: "invoices.csv", required: true },
  { key: "licences", label: "licences.csv", required: false },
  { key: "contracts", label: "contracts_extracted.json", required: false },
];

export default function Connect() {
  const router = useRouter();
  const [mode, setMode] = useState<"demo" | "upload">("demo");
  const [files, setFiles] = useState<Record<string, File>>({});
  const ready = mode === "demo" || (files.vendors && files.invoices);

  const go = () => {
    uploadStore.files = mode === "upload" ? files : undefined;
    router.push("/scan");
  };

  return (
    <div className="mx-auto max-w-4xl p-6 md:p-10">
      <Logo />
      <p className="mt-8 text-sm font-semibold uppercase tracking-wider text-brand">Reuse</p>
      <h1 className="text-3xl font-bold">Connect the data you already have</h1>
      <p className="mt-1 text-muted">No new system. LeakLens reuses your existing exports.</p>

      <div className="mt-6 inline-flex rounded-lg border border-line bg-surface p-1 text-sm">
        {(["demo", "upload"] as const).map((m) => (
          <button key={m} onClick={() => setMode(m)}
            className={`rounded-md px-4 py-1.5 font-medium ${mode === m ? "bg-brand text-white" : "text-muted"}`}>
            {m === "demo" ? "NCBA demo dataset" : "Upload your own files"}
          </button>
        ))}
      </div>

      {mode === "demo" ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {SOURCES.map(({ icon: Icon, name, detail }) => (
            <div key={name} className="card flex items-start gap-3 p-4">
              <Icon className="mt-0.5 text-brand" />
              <div className="flex-1"><div className="font-semibold">{name}</div><div className="text-sm text-muted">{detail}</div></div>
              <CheckCircle2 className="text-brand-2" aria-label="connected" />
            </div>
          ))}
        </div>
      ) : (
        <div className="mt-6 card p-5">
          <p className="text-sm text-muted">Columns are listed in CONTRACT.md. Need a sample? <a className="font-semibold text-brand underline" href="/api/demo-data.zip">Download the demo files</a>.</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {SLOTS.map((s) => (
              <label key={s.key} className="flex cursor-pointer items-center gap-3 rounded-lg border border-dashed border-line p-3 hover:border-brand">
                <Upload size={18} className="text-muted" />
                <span className="flex-1 text-sm">
                  <b>{s.label}</b> {s.required ? <span className="text-risk">required</span> : <span className="text-muted">optional</span>}
                  <br /><span className="text-muted">{files[s.key]?.name ?? "Choose file"}</span>
                </span>
                {files[s.key] && <CheckCircle2 className="text-brand-2" />}
                <input type="file" className="sr-only" accept=".csv,.json"
                  onChange={(e) => e.target.files?.[0] && setFiles({ ...files, [s.key]: e.target.files[0] })} />
              </label>
            ))}
          </div>
        </div>
      )}

      <button disabled={!ready} onClick={go}
        className="mt-8 rounded-xl bg-brand px-6 py-3 text-lg font-semibold text-white shadow disabled:opacity-40">
        Scan 12 months →
      </button>
    </div>
  );
}
