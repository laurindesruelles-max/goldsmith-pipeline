import React from "react";
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing, random} from "remotion";

export const FPS = 30;
export const s = (t: number) => Math.round(t * FPS);
export const AMBER = "#FFB02E";
export const RED = "#EB3434";
export const INK = "#E9ECF2";
export const MUTED = "#8A93A6";
export const BG = "#0B0D12";
export const FONT = "Inter, 'Inter Display', sans-serif";

export const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
export const ease = Easing.bezier(0.22, 1, 0.36, 1);
export const easeIn = Easing.bezier(0.64, 0, 0.78, 0);

/** 0..1 Fortschritt zwischen zwei Zeitpunkten (Sekunden, relativ zur Sequence) */
export const useT = (a: number, b: number, e = ease) => {
  const f = useCurrentFrame();
  return interpolate(f, [s(a), s(b)], [0, 1], {...clamp, easing: e});
};
export const useSpring = (at: number, cfg = {damping: 14, mass: 0.6, stiffness: 140}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return spring({frame: f - s(at), fps, config: cfg});
};

/** Dunkler Hintergrund: Verlauf, Raster mit Scanlines, Vignette, langsames Driften */
export const Backdrop: React.FC<{tint?: string; grid?: boolean; children?: React.ReactNode}> = ({tint = "#121722", grid = true, children}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 40%, ${tint} 0%, ${BG} 70%)`}}>
      {grid && (
        <AbsoluteFill style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
          backgroundSize: "60px 60px", backgroundPosition: `${f * 0.3}px ${f * 0.15}px`,
          maskImage: "radial-gradient(ellipse at center, black 30%, transparent 80%)",
        }} />
      )}
      {children}
      <AbsoluteFill style={{background: "repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0px, rgba(0,0,0,0.12) 1px, transparent 2px, transparent 4px)", opacity: 0.5}} />
      <AbsoluteFill style={{background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.75) 100%)"}} />
    </AbsoluteFill>
  );
};

/** Filmkorn ueber allem */
export const Grain: React.FC = () => {
  const f = useCurrentFrame();
  const seed = Math.floor(f / 2) % 7;
  return (
    <AbsoluteFill style={{pointerEvents: "none", mixBlendMode: "overlay", opacity: 0.22}}>
      <svg width="100%" height="100%">
        <filter id={`g${seed}`}><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={seed} stitchTiles="stitch" /></filter>
        <rect width="100%" height="100%" filter={`url(#g${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

/** Getippter Text mit Cursor */
export const Typed: React.FC<{text: string; at: number; cps?: number; style?: React.CSSProperties; cursor?: boolean}> = ({text, at, cps = 14, style, cursor = true}) => {
  const f = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor(((f - s(at)) / FPS) * cps)));
  if (f < s(at)) return null;
  const blink = Math.floor(f / 8) % 2 === 0;
  return <span style={{fontFamily: FONT, ...style}}>{text.slice(0, n)}{cursor && <span style={{opacity: blink ? 1 : 0, color: AMBER}}>▍</span>}</span>;
};

export const fmt = (n: number) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");

/** Hochzaehlende Zahl */
export const Counter: React.FC<{from?: number; to: number; at: number; dur?: number; prefix?: string; suffix?: string; style?: React.CSSProperties}> = ({from = 0, to, at, dur = 1.2, prefix = "", suffix = "", style}) => {
  const p = useT(at, at + dur, Easing.bezier(0.16, 1, 0.3, 1));
  return <span style={{fontVariantNumeric: "tabular-nums", ...style}}>{prefix}{fmt(from + (to - from) * p)}{suffix}</span>;
};

/** Eingangsbewegung: Pop (Skalierung + Blur) */
export const Pop: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties; from?: number}> = ({at, children, style, from = 0.6}) => {
  const sp = useSpring(at);
  const f = useCurrentFrame();
  if (f < s(at)) return null;
  return <div style={{transform: `scale(${from + (1 - from) * sp})`, opacity: Math.min(1, sp * 1.6), filter: `blur(${(1 - Math.min(1, sp)) * 8}px)`, ...style}}>{children}</div>;
};

/** Szenen-Uebergang: schneller Zoom-Blur rein, raus */
export const Shot: React.FC<{dur: number; children: React.ReactNode; inZoom?: number; outZoom?: number; drift?: number}> = ({dur, children, inZoom = 1.08, outZoom = 1.06, drift = 0.03}) => {
  const f = useCurrentFrame(); const D = s(dur);
  const i = interpolate(f, [0, 7], [1, 0], {...clamp, easing: ease});
  const o = interpolate(f, [D - 5, D], [0, 1], {...clamp, easing: easeIn});
  const slow = interpolate(f, [0, D], [1, 1 + drift], clamp);
  const sc = slow * (1 + (inZoom - 1) * i) * (1 + (outZoom - 1) * o);
  return <AbsoluteFill style={{transform: `scale(${sc})`, filter: `blur(${i * 10 + o * 12}px)`, opacity: 1 - o * 0.3}}>{children}</AbsoluteFill>;
};

/** Kapitel-/Orts-Etikett oben links */
export const Tag: React.FC<{text: string; at?: number; color?: string}> = ({text, at = 0.1, color = AMBER}) => {
  const p = useT(at, at + 0.5);
  return (
    <div style={{position: "absolute", left: 70, top: 60, display: "flex", alignItems: "center", gap: 14, opacity: p, transform: `translateX(${(1 - p) * -30}px)`}}>
      <div style={{width: 12, height: 12, background: color, boxShadow: `0 0 14px ${color}`}} />
      <div style={{fontFamily: FONT, fontWeight: 700, fontSize: 24, letterSpacing: 4, color: INK}}>{text}</div>
    </div>
  );
};

/** Grosse Schlagzeile mit Akzent-Balken */
export const Headline: React.FC<{at: number; lines: string[]; accent?: number; size?: number; color?: string}> = ({at, lines, accent = -1, size = 120, color = AMBER}) => {
  return (
    <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
      {lines.map((l, i) => {
        const sp = useSpring(at + i * 0.12);
        return <div key={i} style={{fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.0, letterSpacing: -2, color: i === accent ? color : INK,
          transform: `translateY(${(1 - sp) * 40}px)`, opacity: Math.min(1, sp * 1.5), textShadow: "0 8px 40px rgba(0,0,0,0.6)"}}>{l}</div>;
      })}
    </div>
  );
};

export const Glitch: React.FC<{at: number; dur?: number; children: React.ReactNode}> = ({at, dur = 0.35, children}) => {
  const f = useCurrentFrame();
  const on = f >= s(at) && f < s(at + dur);
  const k = on ? (random(`g${f}`) - 0.5) : 0;
  return (
    <div style={{position: "relative", transform: `translateX(${k * 30}px)`}}>
      {on && <div style={{position: "absolute", inset: 0, transform: `translateX(${-k * 18}px)`, mixBlendMode: "screen", filter: "drop-shadow(4px 0 0 rgba(255,0,60,0.8))", opacity: 0.8}}>{children}</div>}
      <div style={{clipPath: on ? `inset(${random(`a${f}`) * 40}% 0 ${random(`b${f}`) * 40}% 0)` : undefined}}>{children}</div>
      {on && <div style={{position: "absolute", inset: 0, clipPath: `inset(0 0 ${60 + random(`c${f}`) * 30}% 0)`, transform: `translateX(${k * 50}px)`}}>{children}</div>}
    </div>
  );
};
