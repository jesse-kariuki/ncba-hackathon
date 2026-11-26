"use client";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

// Splash: ring draws, the leak (gold drop) falls into the lens, a scan line sweeps, wordmark rises.
export default function Splash() {
  const router = useRouter();
  useEffect(() => {
    const t = setTimeout(() => router.push("/signin"), 3600);
    return () => clearTimeout(t);
  }, [router]);
  return (
    <button onClick={() => router.push("/signin")} aria-label="Continue"
      className="grid h-screen w-full place-items-center bg-[#0E1F2F] text-white">
      <div className="flex flex-col items-center gap-5">
        <svg width="180" height="180" viewBox="0 0 100 100" className="overflow-visible">
          <motion.circle cx="44" cy="44" r="30" fill="none" stroke="#18A374" strokeWidth="8"
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.9, ease: "easeOut" }} />
          <motion.line x1="66" y1="66" x2="88" y2="88" stroke="#18A374" strokeWidth="10" strokeLinecap="round"
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.85, duration: 0.35 }} />
          <motion.path d="M44 26 C44 26 31 42 31 50 a13 13 0 0 0 26 0 C57 42 44 26 44 26Z" fill="#F2A900"
            initial={{ y: -120, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1.1, duration: 0.7, ease: [0.5, 0, 0.75, 0] }} />
          <motion.rect x="18" y="43" width="52" height="3" rx="1.5" fill="#fff"
            initial={{ opacity: 0, y: -22 }} animate={{ opacity: [0, 0.9, 0], y: 22 }} transition={{ delay: 2.0, duration: 1.1 }} />
        </svg>
        <motion.div className="text-5xl font-extrabold tracking-tight" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 2.3 }}>
          Leak<span className="text-[#18A374]">Lens</span>
        </motion.div>
        <motion.p className="text-[#9FB3C8]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2.7 }}>
          Find the <span className="font-bold text-[#F2A900]">leaks</span> before you pay.
        </motion.p>
      </div>
    </button>
  );
}
