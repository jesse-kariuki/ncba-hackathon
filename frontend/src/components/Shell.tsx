"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, ListChecks, PiggyBank, ScrollText, Settings, Moon, Sun, Upload } from "lucide-react";
import { Logo } from "./Logo";
import { useRole } from "@/lib/role";
import { ROLE_LABEL, type Role } from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/findings", label: "Findings", icon: ListChecks },
  { href: "/savings", label: "Savings", icon: PiggyBank },
  { href: "/audit", label: "Audit log", icon: ScrollText },
  { href: "/connect", label: "New scan", icon: Upload },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const { role, setRole, theme, setTheme } = useRole();
  return (
    <div className="min-h-screen md:grid md:grid-cols-[232px_1fr]">
      <aside className="hidden md:flex flex-col gap-1 border-r border-line bg-surface p-4 sticky top-0 h-screen">
        <Link href="/dashboard" className="mb-6 px-2"><Logo /></Link>
        {NAV.map(({ href, label, icon: Icon }) => {
          const on = path === href || (href !== "/dashboard" && path.startsWith(href));
          return (
            <Link key={href} href={href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium ${on ? "bg-brand text-white" : "text-muted hover:bg-bg"}`}>
              <Icon size={18} /> {label}
            </Link>
          );
        })}
        <div className="mt-auto text-xs text-muted px-2 leading-relaxed">
          <b className="text-ink">Rules decide · AI explains · humans approve.</b><br />Illustrative data only.
        </div>
      </aside>
      <div className="min-w-0">
        <header className="sticky top-0 z-10 flex items-center gap-3 border-b border-line bg-surface/90 backdrop-blur px-4 md:px-8 py-3">
          <span className="md:hidden"><Logo size={24} /></span>
          <span className="hidden sm:inline rounded-full bg-gold/15 px-3 py-1 text-xs font-semibold text-ink">Illustrative data</span>
          <div className="ml-auto flex items-center gap-2">
            <label className="text-xs text-muted hidden sm:block" htmlFor="role">Signed in as</label>
            <select id="role" value={role} onChange={(e) => setRole(e.target.value as Role)}
              className="rounded-lg border border-line bg-surface px-2 py-1.5 text-sm font-semibold">
              {(Object.keys(ROLE_LABEL) as Role[]).map((r) => <option key={r} value={r}>{ROLE_LABEL[r]}</option>)}
            </select>
            <button aria-label="Toggle theme" onClick={() => setTheme(theme === "light" ? "dark" : "light")}
              className="rounded-lg border border-line p-2">{theme === "light" ? <Moon size={16} /> : <Sun size={16} />}</button>
          </div>
        </header>
        <nav className="md:hidden flex gap-1 overflow-x-auto border-b border-line bg-surface px-2 py-2">
          {NAV.map(({ href, label }) => (
            <Link key={href} href={href} className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-sm ${path.startsWith(href) ? "bg-brand text-white" : "text-muted"}`}>{label}</Link>
          ))}
        </nav>
        <main className="mx-auto max-w-7xl p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
