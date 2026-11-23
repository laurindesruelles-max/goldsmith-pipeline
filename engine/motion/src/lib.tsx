// Goldsmith-Handschrift fuer 2D-Motion-Graphics: Ermittlungsakte (Elfenbein-Papier, rote Faeden, Gold, Anton + Schreibmaschine).
import React from "react";
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing, random} from "remotion";

export const FPS = 30;
export const s = (t: number) => Math.round(t * FPS);
export const GOLD = "#DEBC68";
export const RED = "#CD1923";
export const IVORY = "#F2EAD8";
export const INK = "#1C1612";
export const MUTED = "#9C8F7A";
export const BG = "#0E0B09";
export const ANTON = "Anton, sans-serif";
export const TYPE = "'Special Elite', monospace";
export const SANS = "Inter, sans-serif";

export const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
export const ease = Easing.bezier(0.22, 1, 0.36, 1);
export const easeIn = Easing.bezier(0.64, 0, 0.78, 0);

export const useT = (a: number, b: number, e = ease) => interpolate(useCurrentFrame(), [s(a), s(b)], [0, 1], {...clamp, easing: e});
export const useSpring = (at: number, cfg = {damping: 14, mass: 0.6, stiffness: 140}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return spring({frame: f - s(at), fps, config: cfg});
};

/** Dunkler Ermittler-Tisch: warmes Lampenlicht oben links, Papierkorn, Vignette, langsames Driften */
export const Desk: React.FC<{children?: React.ReactNode; warm?: number; red?: boolean}> = ({children, warm = 1, red}) => {
  const f = useCurrentFrame();
  const flick = 1 + 0.03 * Math.sin(f * 0.37) + 0.02 * Math.sin(f * 1.3);
  return (
    <AbsoluteFill style={{background: BG}}>
      <AbsoluteFill style={{background: red
        ? `radial-gradient(ellipse at 50% 45%, rgba(120,20,20,${0.55 * flick}) 0%, transparent 65%)`
        : `radial-gradient(ellipse at 35% 30%, rgba(160,110,50,${0.38 * warm * flick}) 0%, rgba(60,40,22,0.25) 40%, transparent 75%)`}} />
      <AbsoluteFill style={{opacity: 0.08, backgroundImage: "repeating-linear-gradient(90deg, rgba(255,230,190,0.5) 0 1px, transparent 1px 7px)", transform: `translateX(${f * 0.2}px)`}} />
      {children}
      <AbsoluteFill style={{background: "radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.8) 100%)"}} />
    </AbsoluteFill>
  );
};

export const Grain: React.FC = () => {
  const f = useCurrentFrame(); const seed = Math.floor(f / 2) % 7;
  return (
    <AbsoluteFill style={{pointerEvents: "none", mixBlendMode: "overlay", opacity: 0.28}}>
      <svg width="100%" height="100%"><filter id={`g${seed}`}><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed={seed} /></filter>
        <rect width="100%" height="100%" filter={`url(#g${seed})`} /></svg>
    </AbsoluteFill>
  );
};

/** Schreibmaschinentext (Tastatursound kommt aus motion_fx.py, gleiche Geschwindigkeit) */
export const CPS = 18;
export const Typed: React.FC<{text: string; at: number; style?: React.CSSProperties; cursor?: boolean}> = ({text, at, style, cursor = true}) => {
  const f = useCurrentFrame();
  if (f < s(at)) return null;
  const n = Math.min(text.length, Math.floor(((f - s(at)) / FPS) * CPS));
  return <span style={{fontFamily: TYPE, ...style}}>{text.slice(0, n)}{cursor && n < text.length && <span style={{opacity: Math.floor(f / 6) % 2 ? 1 : 0}}>_</span>}</span>;
};

export const fmt = (n: number, dec = 0) => {
  const v = dec ? n.toFixed(dec) : Math.round(n).toString();
  const [a, b] = v.split("."); return a.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (b ? "." + b : "");
};
export const Counter: React.FC<{to: number; at: number; dur?: number; prefix?: string; suffix?: string; dec?: number; style?: React.CSSProperties}> = ({to, at, dur = 1.2, prefix = "", suffix = "", dec = 0, style}) => {
  const p = useT(at, at + dur, Easing.bezier(0.16, 1, 0.3, 1));
  return <span style={{fontVariantNumeric: "tabular-nums", ...style}}>{prefix}{fmt(to * p, dec)}{suffix}</span>;
};

export const Pop: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties; from?: number}> = ({at, children, style, from = 0.6}) => {
  const sp = useSpring(at); const f = useCurrentFrame();
  if (f < s(at)) return null;
  return <div style={{transform: `scale(${from + (1 - from) * sp})`, opacity: Math.min(1, sp * 1.6), filter: `blur(${(1 - Math.min(1, sp)) * 8}px)`, ...style}}>{children}</div>;
};

/** Akten-Etikett oben links (Schreibmaschine auf Papierstreifen) */
export const Label: React.FC<{text?: string; at?: number}> = ({text, at = 0.1}) => {
  const p = useT(at, at + 0.5);
  if (!text) return null;
  return (
    <div style={{position: "absolute", left: 80, top: 64, opacity: p, transform: `translateX(${(1 - p) * -30}px) rotate(-1.2deg)`,
      background: IVORY, padding: "8px 22px", boxShadow: "0 6px 20px rgba(0,0,0,0.6)"}}>
      <span style={{fontFamily: TYPE, fontSize: 28, color: INK, letterSpacing: 3}}>{text}</span>
    </div>
  );
};

/** Grosse Anton-Zeile */
export const Big: React.FC<{at: number; text: string; color?: string; size?: number}> = ({at, text, color = IVORY, size = 130}) => {
  const sp = useSpring(at); const f = useCurrentFrame();
  if (f < s(at)) return null;
  return <div style={{fontFamily: ANTON, fontSize: size, color, lineHeight: 1, letterSpacing: 1, textTransform: "uppercase",
    transform: `translateY(${(1 - sp) * 40}px)`, opacity: Math.min(1, sp * 1.5), textShadow: "0 10px 40px rgba(0,0,0,0.7)"}}>{text}</div>;
};

/** Langsame Kamera-Drift + Einstiegs-Zoom ueber die ganze Grafik */
export const Drift: React.FC<{len: number; children: React.ReactNode}> = ({len, children}) => {
  const f = useCurrentFrame();
  const i = interpolate(f, [0, 8], [1, 0], {...clamp, easing: ease});
  const sc = interpolate(f, [0, s(len)], [1, 1.04], clamp) * (1 + 0.06 * i);
  return <AbsoluteFill style={{transform: `scale(${sc})`, filter: `blur(${i * 8}px)`}}>{children}</AbsoluteFill>;
};

export const Glitch: React.FC<{at: number; dur?: number; children: React.ReactNode}> = ({at, dur = 0.35, children}) => {
  const f = useCurrentFrame(); const on = f >= s(at) && f < s(at + dur);
  const k = on ? random(`g${f}`) - 0.5 : 0;
  return (
    <div style={{position: "relative", transform: `translateX(${k * 30}px)`}}>
      {on && <div style={{position: "absolute", inset: 0, transform: `translateX(${-k * 18}px)`, filter: "drop-shadow(4px 0 0 rgba(255,0,40,0.8))", opacity: 0.8}}>{children}</div>}
      <div style={{clipPath: on ? `inset(${random(`a${f}`) * 40}% 0 ${random(`b${f}`) * 40}% 0)` : undefined}}>{children}</div>
    </div>
  );
};

/** Einfache Icons (Linien, Elfenbein) */
export const Icon: React.FC<{name: string; size?: number; color?: string}> = ({name, size = 90, color = IVORY}) => {
  const sw = 6; const st = {fill: "none", stroke: color, strokeWidth: sw, strokeLinecap: "round" as const, strokeLinejoin: "round" as const};
  const P: Record<string, React.ReactNode> = {
    phone: <><rect x={28} y={8} width={44} height={84} rx={9} {...st} /><circle cx={50} cy={80} r={3} fill={color} /></>,
    server: <>{[12, 40, 68].map((y) => <g key={y}><rect x={12} y={y} width={76} height={22} rx={4} {...st} /><circle cx={74} cy={y + 11} r={4} fill={color} /></g>)}</>,
    bank: <><path d="M10 38 L50 12 L90 38 Z" {...st} /><path d="M18 84 H82 M22 44 V76 M40 44 V76 M60 44 V76 M78 44 V76" {...st} /></>,
    factory: <><path d="M10 88 V44 L34 58 V44 L58 58 V24 H76 V88 Z" {...st} /></>,
    person: <><circle cx={50} cy={32} r={16} {...st} /><path d="M18 90 C18 64 82 64 82 90" {...st} /></>,
    ship: <><path d="M10 62 H90 L78 84 H22 Z M30 62 V40 H62 V62 M46 40 V22" {...st} /></>,
    money: <><rect x={8} y={26} width={84} height={48} rx={6} {...st} /><circle cx={50} cy={50} r={12} {...st} /></>,
    doc: <><path d="M24 8 H62 L78 24 V92 H24 Z M62 8 V24 H78 M34 46 H68 M34 60 H68 M34 74 H56" {...st} /></>,
    store: <><path d="M12 40 L20 14 H80 L88 40 Z M18 40 V88 H82 V40 M40 88 V62 H60 V88" {...st} /></>,
    lock: <><rect x={22} y={44} width={56} height={44} rx={6} {...st} /><path d="M34 44 V30 a16 16 0 0 1 32 0 V44" {...st} /></>,
    eye: <><path d="M8 50 C28 18 72 18 92 50 C72 82 28 82 8 50 Z" {...st} /><circle cx={50} cy={50} r={12} fill={color} /></>,
    gavel: <><path d="M30 20 L58 48 M44 6 L72 34 M37 13 L65 41 M51 41 L84 74" {...st} /><path d="M14 92 H58" {...st} /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 100 100">{P[name] || P.doc}</svg>;
};

/** Roter Faden (leicht durchhaengend), waechst von a nach b */
export const Thread: React.FC<{x1: number; y1: number; x2: number; y2: number; p: number; sag?: number; color?: string; width?: number}> = ({x1, y1, x2, y2, p, sag = 0.12, color = RED, width = 3.5}) => {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 + Math.hypot(x2 - x1, y2 - y1) * sag;
  const len = Math.hypot(x2 - x1, y2 - y1) * 1.15;
  return <path d={`M${x1},${y1} Q${mx},${my} ${x2},${y2}`} fill="none" stroke={color} strokeWidth={width} strokeDasharray={len} strokeDashoffset={len * (1 - p)}
    style={{filter: "drop-shadow(0 3px 3px rgba(0,0,0,0.6))"}} />;
};

/** Stecknadel (rot) */
export const PushPin: React.FC<{x: number; y: number; k: number; color?: string}> = ({x, y, k, color = RED}) => (
  <g transform={`translate(${x},${y}) scale(${k})`}>
    <ellipse cx={4} cy={6} rx={10} ry={5} fill="rgba(0,0,0,0.45)" />
    <circle r={11} fill={color} /><circle cx={-3} cy={-4} r={4} fill="rgba(255,255,255,0.55)" />
  </g>
);
