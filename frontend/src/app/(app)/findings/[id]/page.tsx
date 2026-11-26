"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, Bot, Gavel, Lock, Mail, X } from "lucide-react";
import { api, ACTIONS, kes, kesFull, ROLE_LABEL, type Finding } from "@/lib/api";
import { useRole } from "@/lib/role";
import { ErrorBox, Loading, Severity, Status } from "@/components/ui";

function useExplanation(id: string) {
  const [text, setText] = useState("");
  const [source, setSource] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  useEffect(() => {
    let closed = false;
    setText(""); setSource(null);
    const es = new EventSource(`/api/findings/${id}/explain/stream`);
    es.onmessage = (e) => {
      if (closed) return;
      const d = JSON.parse(e.data);
      if (d.token) setText((t) => t + d.token);
      if (d.done) { setSource(d.source); setEmail(d.vendor_email); es.close(); }
    };
    // If streaming fails (proxy, network), fall back to the plain JSON endpoint so the box never hangs.
    es.onerror = () => {
      es.close();
      if (closed) return;
      fetch(`/api/findings/${id}/explain`).then((r) => r.json()).then((x) => {
        if (closed) return;
        setText(x.explanation); setSource(x.source ?? "template"); setEmail(x.vendor_email);
      }).catch(() => {});
    };
    return () => { closed = true; es.close(); };
  }, [id]);
  return { text, source, email, setEmail };
}

// Highlight evidence values that appear in every row (e.g. the shared eTIMS number) for side-by-side duplicates.
function sharedTokens(f: Finding) {
  const sets = f.evidence.filter((e) => e.label.startsWith("INV")).map((e) => new Set(e.detail.split(" · ")));
  if (sets.length < 2) return new Set<string>();
  return new Set([...sets[0]].filter((t) => sets.every((s) => s.has(t)) && !t.startsWith("paid")));
}

export default function FindingDetail() {
  const { id } = useParams<{ id: string }>();
  const { role } = useRole();
  const [f, setF] = useState<Finding | null>(null);
  const [err, setErr] = useState("");
  const [comment, setComment] = useState("");
  const [toast, setToast] = useState("");
  const [drawer, setDrawer] = useState(false);
  const ex = useExplanation(id);
  useEffect(() => { api.finding(id).then(setF).catch((e) => setErr(e.message)); }, [id]);

  if (err) return <ErrorBox msg={err} />;
  if (!f) return <Loading />;
  const isDup = f.detector === "D1_duplicate";
  const shared = sharedTokens(f);
  const invRows = f.evidence.filter((e) => e.label.startsWith("INV"));
  const otherRows = isDup ? f.evidence.filter((e) => !e.label.startsWith("INV")) : f.evidence;

  const decide = async (d: "approved" | "rejected") => {
    try {
      setF(await api.decide(f.finding_id, role, d, comment));
      setToast(`${d === "approved" ? "Approved" : "Rejected"} · written to the audit trail`);
      setTimeout(() => setToast(""), 3500);
    } catch (e: any) { setToast(e.message); setTimeout(() => setToast(""), 3500); }
  };

  return (
    <div className="space-y-5">
      <Link href="/findings" className="inline-flex items-center gap-1 text-sm text-muted hover:text-brand"><ArrowLeft size={16} /> All findings</Link>
      <header className="flex flex-wrap items-start gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2"><Severity s={f.severity} /><Status s={f.status} /><span className="text-xs text-muted">{f.finding_id}</span></div>
          <h1 className="mt-2 text-2xl font-bold md:text-3xl">{f.title}</h1>
          <Link href={`/vendors/${f.vendor_id}`} className="text-brand underline-offset-2 hover:underline">{f.vendor_name} → Vendor 360</Link>
        </div>
        <div className="text-right">
          <div className="text-3xl font-extrabold text-brand">{f.kes_impact ? kesFull(f.kes_impact) : "Compliance risk"}</div>
          <div className="text-xs text-muted">{f.kes_impact ? "avoidable" : "no direct cost"}</div>
        </div>
      </header>

      <section className="card p-5">
        <h2 className="font-semibold">Evidence</h2>
        {isDup && invRows.length >= 2 && (
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {invRows.map((e) => (
              <div key={e.label} className="rounded-xl border border-line p-4">
                <div className="font-mono text-lg font-bold">{e.label}</div>
                <ul className="mt-2 space-y-1 text-sm">
                  {e.detail.split(" · ").map((t) => (
                    <li key={t} className={shared.has(t) ? "rounded bg-gold/25 px-1 font-semibold" : ""}>{t}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
        {otherRows.length > 0 && (
          <dl className="mt-3 grid gap-x-6 gap-y-2 sm:grid-cols-2">
            {otherRows.map((e) => (
              <div key={e.label} className="flex justify-between gap-4 border-b border-line py-2 text-sm">
                <dt className="text-muted">{e.label}</dt><dd className="text-right font-medium">{e.detail}</dd>
              </div>
            ))}
          </dl>
        )}
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-xl border border-rule/25 bg-rule/5 p-5">
          <div className="flex items-center gap-2 font-semibold text-rule"><Gavel size={18} /> Why the rules flagged it</div>
          <p className="mt-2">{f.rule_reason}</p>
          <p className="mt-2 text-xs text-muted">Deterministic rule · confidence {Math.round(f.confidence * 100)}% · the AI cannot change this decision</p>
        </section>
        <section className="rounded-xl border border-brand/25 bg-brand/5 p-5">
          <div className="flex items-center gap-2 font-semibold text-brand"><Bot size={18} /> Explanation ({ex.source === "gemini" ? "AI · Gemini" : ex.source === "claude" ? "AI · Claude" : ex.source ? "template" : "writing…"})</div>
          <p className="mt-2 min-h-12">{ex.text}<span className={ex.source ? "hidden" : "animate-pulse"}>▍</span></p>
        </section>
      </div>

      <section className="card p-5">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="mr-auto font-semibold">Action: {ACTIONS[f.suggested_action]}</h2>
          <button onClick={() => setDrawer(true)} disabled={!ex.email}
            className="inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm font-medium disabled:opacity-40"><Mail size={16} /> Draft email to vendor</button>
        </div>
        {f.status !== "open" ? (
          <p className="mt-3 rounded-lg bg-brand/10 p-3 text-brand">This finding was {f.status}. See the audit log.</p>
        ) : role === "procurement_manager" ? (
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <input value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Comment for the audit trail (optional)"
              className="min-w-60 flex-1 rounded-lg border border-line bg-surface px-3 py-2 text-sm" />
            <button onClick={() => decide("approved")} className="rounded-lg bg-brand px-4 py-2 font-semibold text-white">Approve: {ACTIONS[f.suggested_action]}</button>
            <button onClick={() => decide("rejected")} className="rounded-lg border border-line px-4 py-2 font-semibold">Reject</button>
          </div>
        ) : (
          <p className="mt-3 flex items-center gap-2 rounded-lg bg-gold/15 p-3 text-sm">
            <Lock size={16} /> Signed in as <b>{ROLE_LABEL[role]}</b>. This needs <b>Procurement manager</b> approval. Nothing is paid, held or cancelled automatically.
          </p>
        )}
      </section>

      <AnimatePresence>
        {drawer && (
          <motion.div className="fixed inset-0 z-30 flex justify-end bg-black/30" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setDrawer(false)}>
            <motion.aside initial={{ x: 480 }} animate={{ x: 0 }} exit={{ x: 480 }} transition={{ type: "spring", damping: 26 }}
              onClick={(e) => e.stopPropagation()} className="h-full w-full max-w-lg overflow-y-auto bg-surface p-6 shadow-xl">
              <div className="flex items-center"><h2 className="text-lg font-semibold">Email to {f.vendor_name}</h2>
                <button aria-label="Close" className="ml-auto" onClick={() => setDrawer(false)}><X /></button></div>
              <textarea value={ex.email} onChange={(e) => ex.setEmail(e.target.value)} rows={18}
                className="mt-4 w-full rounded-lg border border-line bg-bg p-3 font-mono text-sm" />
              <button onClick={() => { navigator.clipboard?.writeText(ex.email); setToast("Email copied"); setTimeout(() => setToast(""), 2500); }}
                className="mt-3 rounded-lg bg-brand px-4 py-2 font-semibold text-white">Copy email</button>
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {toast && <motion.div initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 40, opacity: 0 }}
          className="fixed bottom-6 left-1/2 z-40 -translate-x-1/2 rounded-xl bg-ink px-5 py-3 text-sm font-medium text-white shadow-lg" role="status">{toast}</motion.div>}
      </AnimatePresence>
    </div>
  );
}
