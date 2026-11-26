"use client";
import { useRouter } from "next/navigation";
import { ShieldCheck, Receipt, LineChart } from "lucide-react";
import { Logo } from "@/components/Logo";
import { useRole } from "@/lib/role";
import type { Role } from "@/lib/api";

const ROLES: { role: Role; title: string; desc: string; icon: any }[] = [
  { role: "ap_officer", title: "AP officer", desc: "Sees warnings before paying. Cannot approve actions.", icon: Receipt },
  { role: "procurement_manager", title: "Procurement manager", desc: "Reviews findings, approves holds and cancellations, emails vendors.", icon: ShieldCheck },
  { role: "cfo", title: "CFO", desc: "One number, the trend, and what has been recovered.", icon: LineChart },
];

export default function SignIn() {
  const router = useRouter();
  const { setRole } = useRole();
  return (
    <div className="grid min-h-screen place-items-center p-6">
      <div className="w-full max-w-3xl">
        <Logo size={36} />
        <h1 className="mt-8 text-3xl font-bold">Sign in</h1>
        <p className="mt-1 text-muted">Choose a role for the demo. Every action is tied to a role in the audit log.</p>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {ROLES.map(({ role, title, desc, icon: Icon }) => (
            <button key={role} onClick={() => { setRole(role); router.push("/connect"); }}
              className="card p-5 text-left transition hover:-translate-y-0.5 hover:border-brand focus:outline-2 focus:outline-brand">
              <Icon className="text-brand" />
              <div className="mt-3 font-semibold">{title}</div>
              <div className="mt-1 text-sm text-muted">{desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
