"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { animate, motion } from "framer-motion";
import { CheckCircle2, Loader2 } from "lucide-react";
import { Logo } from "@/components/Logo";
import { api, kes, uploadStore, type Summary } from "@/lib/api";

const STEPS = ["Matching invoices…", "Checking KRA eTIMS numbers…", "Reading contracts…", "Counting active licence seats…",
  "Looking for spending anomalies…", "Checking vendor risk…"];

export default function Scan() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [counter, setCounter] = useState(0);
  const [err, setErr] = useState("");
  const [result, setResult] = useState<Summary | null>(null);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    api.scan(uploadStore.files).then(setResult).catch((e) => setErr(e.message));
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length)), 650);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!result) return;
    const c = animate(0, result.total_kes, { duration: 3.6, ease: "easeOut", onUpdate: (v) => setCounter(v) });
    return () => c.stop();
  }, [result]);

  const done = step >= STEPS.length && result;
  useEffect(() => {
    if (done) { const t = setTimeout(() => router.push("/dashboard"), 1400); return () => clearTimeout(t); }
  }, [done, router]);

  const labels = result
    ? [`Matching ${result.scan.n_invoices.toLocaleString()} invoices…`, STEPS[1], `Reading ${result.scan.n_contracts} contracts…`, STEPS[3], STEPS[4], STEPS[5]]
    : STEPS;

  return (
    <div className="grid min-h-screen place-items-center p-6">
      <div className="w-full max-w-xl">
        <Logo />
        <p className="mt-8 text-sm font-semibold uppercase tracking-wider text-brand">Automate</p>
        <h1 className="text-3xl font-bold">Scanning 12 months of spend</h1>
        <div className="card mt-6 p-5">
          <ul className="space-y-3">
            {labels.map((s, i) => (
              <motion.li key={i} initial={{ opacity: 0.3 }} animate={{ opacity: i <= step ? 1 : 0.3 }} className="flex items-center gap-3">
                {i < step ? <CheckCircle2 className="text-brand-2" /> : i === step ? <Loader2 className="animate-spin text-muted" /> : <span className="h-6 w-6 rounded-full border border-line" />}
                <span className={i < step ? "font-medium" : "text-muted"}>{s}</span>
              </motion.li>
            ))}
          </ul>
          <div className="mt-6 border-t border-line pt-4">
            <div className="text-sm text-muted">Avoidable spend found so far</div>
            <div className="text-4xl font-extrabold text-gold">{kes(counter)}</div>
          </div>
        </div>
        {err && <p className="mt-4 rounded-lg bg-risk/10 p-3 text-risk">Scan failed: {err} <button className="underline" onClick={() => router.push("/connect")}>Back</button></p>}
      </div>
    </div>
  );
}
