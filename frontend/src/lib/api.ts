export type Evidence = { label: string; detail: string };
export type Finding = {
  finding_id: string;
  detector: string;
  category: string;
  title: string;
  vendor_id: string;
  vendor_name: string;
  kes_impact: number;
  confidence: number;
  severity: "high" | "medium" | "low";
  evidence: Evidence[];
  rule_reason: string;
  suggested_action: string;
  status: "open" | "approved" | "rejected";
};
export type Category = { key: string; label: string; count: number; kes: number; high: number };
export type Summary = {
  scan: { id: number; created: string; source: string; n_invoices: number; n_vendors: number; n_contracts: number; n_licences: number; seconds: number };
  total_kes: number;
  n_findings: number;
  high_risk_vendors: number;
  categories: Category[];
  top_actions: { finding_id: string; title: string; vendor_name: string; kes_impact: number; suggested_action: string }[];
  savings: { found_kes: number; approved_kes: number; approved_count: number; rejected_count: number; open_count: number };
  theme: Record<"reuse" | "automate" | "reduce" | "eliminate", string>;
};
export type AuditRow = { id: number; ts: string; finding_id: string; action: string; role: string; user: string; decision: string; comment: string; kes_impact: number };
export type Role = "ap_officer" | "procurement_manager" | "cfo";

async function j<T>(r: Response): Promise<T> {
  if (!r.ok) {
    let msg = `${r.status}`;
    try { msg = (await r.json()).detail ?? msg; } catch {}
    throw new Error(msg);
  }
  return r.json();
}

export const api = {
  health: () => fetch("/api/health").then(j<{ ok: boolean; ai_providers: string[] }>),
  summary: () => fetch("/api/summary", { cache: "no-store" }).then(j<Summary>),
  findings: (category?: string) => fetch(`/api/findings${category ? `?category=${category}` : ""}`, { cache: "no-store" }).then(j<Finding[]>),
  finding: (id: string) => fetch(`/api/findings/${id}`, { cache: "no-store" }).then(j<Finding>),
  decide: (id: string, role: Role, decision: "approved" | "rejected", comment = "") =>
    fetch(`/api/findings/${id}/decision`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role, decision, comment }) }).then(j<Finding>),
  audit: () => fetch("/api/audit", { cache: "no-store" }).then(j<AuditRow[]>),
  vendor: (id: string) => fetch(`/api/vendors/${id}`, { cache: "no-store" }).then(j<any>),
  scan: (files?: Record<string, File>) => {
    const fd = new FormData();
    Object.entries(files ?? {}).forEach(([k, f]) => fd.append(k, f));
    return fetch("/api/scan", { method: "POST", body: fd }).then(j<Summary>);
  },
  reset: () => fetch("/api/reset", { method: "POST" }).then(j<{ ok: boolean }>),
};

export const kes = (x: number) => (x >= 1e6 ? `KES ${(x / 1e6).toFixed(1)}m` : x >= 1e3 ? `KES ${Math.round(x / 1e3).toLocaleString()}k` : `KES ${x.toLocaleString()}`);
export const kesFull = (x: number) => `KES ${Math.round(x).toLocaleString()}`;

export const ACTIONS: Record<string, string> = {
  hold_payment: "Hold payment", request_credit_note: "Request credit note", cancel_seats: "Cancel idle seats",
  consolidate_vendor: "Consolidate vendor", give_notice: "Give notice", renegotiate: "Renegotiate",
  request_addendum: "Request addendum", investigate: "Refer to internal audit",
};
export const ROLE_LABEL: Record<Role, string> = { ap_officer: "AP officer", procurement_manager: "Procurement manager", cfo: "CFO" };
export const CAT_ORDER = ["duplicates", "overlap", "contracts", "anomalies", "risk"];

// Files picked on /connect, handed to /scan via client-side navigation.
export const uploadStore: { files?: Record<string, File> } = {};
