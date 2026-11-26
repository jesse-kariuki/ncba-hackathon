"use client";
import { createContext, useContext, useEffect, useState } from "react";
import type { Role } from "./api";

type Ctx = { role: Role; setRole: (r: Role) => void; theme: "light" | "dark"; setTheme: (t: "light" | "dark") => void };
const RoleCtx = createContext<Ctx>({ role: "procurement_manager", setRole: () => {}, theme: "light", setTheme: () => {} });

function read<T extends string>(k: string, d: T): T {
  try { return (localStorage.getItem(k) as T) || d; } catch { return d; }
}
function write(k: string, v: string) {
  try { localStorage.setItem(k, v); } catch {}
}

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<Role>("procurement_manager");
  const [theme, setThemeState] = useState<"light" | "dark">("light");
  useEffect(() => {
    setRoleState(read("ll-role", "procurement_manager"));
    setThemeState(read("ll-theme", "light"));
  }, []);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  const setRole = (r: Role) => { setRoleState(r); write("ll-role", r); };
  const setTheme = (t: "light" | "dark") => { setThemeState(t); write("ll-theme", t); };
  return <RoleCtx.Provider value={{ role, setRole, theme, setTheme }}>{children}</RoleCtx.Provider>;
}
export const useRole = () => useContext(RoleCtx);
