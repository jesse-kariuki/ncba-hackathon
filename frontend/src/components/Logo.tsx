export function LogoMark({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 96 96" aria-hidden="true">
      <circle cx="40" cy="40" r="28" fill="none" stroke="var(--brand)" strokeWidth="8" />
      <line x1="60" y1="60" x2="82" y2="82" stroke="var(--brand)" strokeWidth="10" strokeLinecap="round" />
      <path d="M40 22 C40 22 28 37 28 45 a12 12 0 0 0 24 0 C52 37 40 22 40 22Z" fill="var(--gold)" />
    </svg>
  );
}

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <span className="inline-flex items-center gap-2 font-extrabold tracking-tight" style={{ fontSize: size * 0.8 }}>
      <LogoMark size={size} />
      <span>Leak<span className="text-brand">Lens</span></span>
    </span>
  );
}
