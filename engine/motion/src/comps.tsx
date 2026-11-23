// Goldsmith-Motion-Bausteine. Zeitpunkte hier und in engine/motion_fx.py (Sounds) muessen zusammenpassen!
import React, {useMemo} from "react";
import {AbsoluteFill, interpolate, useCurrentFrame, random, Easing} from "remotion";
import {geoNaturalEarth1, geoMercator, geoPath, geoCentroid} from "d3-geo";
import {feature} from "topojson-client";
// @ts-ignore
import world from "world-atlas/countries-50m.json";
import {s, clamp, ease, GOLD, RED, IVORY, INK, MUTED, ANTON, TYPE, SANS, Desk, Typed, Counter, Pop, Label, Big, Glitch, Icon, Thread, PushPin, useT, useSpring, fmt} from "./lib";

const W = 1920, H = 1080;
// @ts-ignore
const feats: any[] = (feature(world, world.objects.countries) as any).features.filter((d: any) => d.id !== "010");
const byId = (id: string) => feats.find((d) => d.id === id);

/* ======================= MAP: Karte mit Stecknadeln, roten Faeden, Schwarm, Hervorhebung ======================= */
export type MapProps = {label?: string; title?: string; view?: "world" | "europe" | [number, number, number];
  pins?: {id?: string; lonlat?: [number, number]; label?: string}[]; threads?: [number, number][] | "chain" | "none";
  swarm?: number; highlight?: string[]; counter?: {value: number; label: string; prefix?: string; suffix?: string}; pulse?: boolean};
export const MAP_T = {pin: (i: number) => 0.45 + i * 0.55, swarm: [0.2, 1.6], hl: (i: number, n: number) => 0.3 + (i / Math.max(1, n)) * 1.1, counter: 0.4};
export const MapC: React.FC<MapProps> = ({label, title, view = "world", pins = [], threads = "chain", swarm = 0, highlight = [], counter, pulse}) => {
  const f = useCurrentFrame();
  const proj = useMemo(() => {
    if (view === "world") return geoNaturalEarth1().fitExtent([[90, 120], [W - 90, H - 60]], {type: "FeatureCollection", features: feats} as any);
    if (view === "europe") return geoMercator().center([12, 52]).scale(1100).translate([W / 2, H / 2 + 40]);
    return geoMercator().center([view[0], view[1]]).scale(view[2]).translate([W / 2, H / 2 + 40]);
  }, [JSON.stringify(view)]);
  const path = useMemo(() => geoPath(proj), [proj]);
  const ds = useMemo(() => feats.map((d) => ({id: d.id, d: path(d) || ""})), [path]);
  const pts = pins.map((p) => proj(p.lonlat || (geoCentroid(byId(p.id!)) as any)) as [number, number]);
  const sw = useMemo(() => {
    if (!swarm) return [];
    const big = feats.map((d) => ({c: proj(geoCentroid(d)) as [number, number], a: path.area(d)})).filter((x) => x.c && x.a > 60 && x.c[0] > 0 && x.c[0] < W);
    const tot = big.reduce((a, b) => a + Math.sqrt(b.a), 0);
    return Array.from({length: swarm}).map((_, k) => {
      let r = random(`p${k}`) * tot, pick = big[0];
      for (const b of big) { r -= Math.sqrt(b.a); if (r <= 0) { pick = b; break; } }
      const rad = Math.sqrt(pick.a) * 0.35;
      return {x: pick.c[0] + (random(`x${k}`) - 0.5) * rad, y: pick.c[1] + (random(`y${k}`) - 0.5) * rad, t: random(`t${k}`)};
    });
  }, [swarm, proj, path]);
  const pairs: [number, number][] = threads === "none" ? [] : threads === "chain" ? pins.slice(1).map((_, i) => [i, i + 1] as [number, number]) : threads;
  return (
    <Desk>
      <AbsoluteFill>
        <svg width={W} height={H}>
          <defs><filter id="gl"><feGaussianBlur stdDeviation="4" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter></defs>
          {ds.map((p) => {
            const i = highlight.indexOf(p.id);
            const ho = i >= 0 ? interpolate(f, [s(MAP_T.hl(i, highlight.length)), s(MAP_T.hl(i, highlight.length)) + 8], [0, 1], clamp) : 0;
            return <path key={p.id} d={p.d} fill={ho ? `rgba(205,25,35,${0.25 + 0.45 * ho})` : "#2a221b"} stroke={ho ? RED : "#4a3d30"} strokeWidth={ho ? 1.6 : 0.8} />;
          })}
          {sw.map((p, i) => {
            const at = s(MAP_T.swarm[0]) + p.t * s(MAP_T.swarm[1] - MAP_T.swarm[0]);
            const o = interpolate(f, [at, at + 5], [0, 1], clamp), ring = interpolate(f, [at, at + 14], [0, 1], clamp);
            return <g key={i} opacity={o}><circle cx={p.x} cy={p.y} r={2.6} fill={GOLD} filter="url(#gl)" />
              {ring < 1 && <circle cx={p.x} cy={p.y} r={2 + ring * 14} fill="none" stroke={GOLD} strokeOpacity={1 - ring} strokeWidth={1.4} />}</g>;
          })}
          {pairs.map(([a, b], k) => {
            if (!pts[a] || !pts[b]) return null;
            const t0 = MAP_T.pin(Math.max(a, b)) - 0.35;
            const pr = interpolate(f, [s(t0), s(t0 + 0.5)], [0, 1], {...clamp, easing: ease});
            return <Thread key={k} x1={pts[a][0]} y1={pts[a][1]} x2={pts[b][0]} y2={pts[b][1]} p={pr} sag={0.08} />;
          })}
          {pins.map((p, i) => {
            const t0 = MAP_T.pin(i); const k = interpolate(f, [s(t0), s(t0) + 6], [1.8, 1], {...clamp, easing: ease});
            if (f < s(t0)) return null;
            const pu = pulse ? ((f - s(t0)) % 24) / 24 : 1;
            return <g key={i}>{pulse && <circle cx={pts[i][0]} cy={pts[i][1]} r={12 + pu * 40} fill="none" stroke={RED} strokeOpacity={1 - pu} strokeWidth={3} />}
              <PushPin x={pts[i][0]} y={pts[i][1]} k={k} /></g>;
          })}
        </svg>
        {pins.map((p, i) => p.label && f >= s(MAP_T.pin(i) + 0.15) ? (
          <div key={i} style={{position: "absolute", left: pts[i][0] + 22, top: pts[i][1] - 58, background: IVORY, padding: "4px 14px", transform: "rotate(-1.5deg)", boxShadow: "0 6px 16px rgba(0,0,0,0.6)"}}>
            <Typed text={p.label} at={MAP_T.pin(i) + 0.15} style={{fontSize: 30, color: INK}} />
          </div>) : null)}
      </AbsoluteFill>
      <Label text={label} />
      {title && <div style={{position: "absolute", left: 80, top: 130}}><Big at={0.15} text={title} size={100} /></div>}
      {counter && <div style={{position: "absolute", left: 0, right: 0, bottom: 70, display: "flex", justifyContent: "center"}}>
        <div style={{background: "rgba(14,11,9,0.85)", padding: "8px 36px", borderLeft: `8px solid ${RED}`, display: "flex", alignItems: "baseline", gap: 22}}>
          <span style={{fontFamily: ANTON, fontSize: 104, color: IVORY}}><Counter to={counter.value} at={MAP_T.counter} prefix={counter.prefix} suffix={counter.suffix} /></span>
          <span style={{fontFamily: TYPE, fontSize: 40, color: GOLD}}>{counter.label}</span></div></div>}
    </Desk>
  );
};

/* ======================= FLOW: Ablauf mit Fortschrittsbalken, Paket wandert, optionaler Abzweig ======================= */
export type FlowProps = {label?: string; steps?: string[]; nodes: {label: string; icon: string}[]; packet?: "envelope" | "money" | "doc";
  branch?: {after: number; label: string; icon: string; text: string}};
export const FLOW_T = {node: (i: number) => 0.1 + i * 0.15, go: 0.6, seg: 0.75, branchAt: (after: number) => 0.6 + 0.75 * (after + 0.5)};
export const FlowC: React.FC<FlowProps & {len: number}> = ({label, steps, nodes, packet = "envelope", branch, len}) => {
  const f = useCurrentFrame(); const n = nodes.length;
  const xs = nodes.map((_, i) => 260 + (i * (W - 520)) / Math.max(1, n - 1)); const y = 470;
  const tAll = FLOW_T.go + FLOW_T.seg * (n - 1);
  const g = interpolate(f, [s(FLOW_T.go), s(tAll)], [0, n - 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const seg = Math.min(n - 2, Math.floor(g)); const px = xs[seg] + (xs[seg + 1] - xs[seg]) * (g - seg);
  const prog = interpolate(f, [0, s(len * 0.85)], [0, 1], clamp);
  const bx = branch ? (xs[branch.after] + xs[branch.after + 1]) / 2 : 0; const by = 860;
  const bt = branch ? FLOW_T.branchAt(branch.after) : 0;
  const sp = branch ? interpolate(f, [s(bt), s(bt + 0.8)], [0, 1], {...clamp, easing: ease}) : 0;
  const pk = (x: number, yy: number, col: string) => (
    <g transform={`translate(${x - 36},${yy - 26})`}>
      {packet === "money" ? <><rect width={72} height={44} rx={5} fill="#5d7a4a" stroke={IVORY} strokeWidth={3} /><circle cx={36} cy={22} r={9} fill="none" stroke={IVORY} strokeWidth={3} /></>
        : packet === "doc" ? <><rect x={14} width={44} height={56} fill={IVORY} /><path d="M22 16 H50 M22 28 H50 M22 40 H42" stroke={INK} strokeWidth={3} /></>
        : <><rect width={72} height={50} rx={5} fill={col} /><path d="M3 5 L36 30 L69 5" fill="none" stroke={INK} strokeWidth={4} /></>}
    </g>);
  return (
    <Desk>
      <Label text={label} />
      {steps && <>
        <div style={{position: "absolute", left: 80, right: 80, top: 150, height: 6, background: "#3a3027"}}>
          <div style={{width: `${prog * 100}%`, height: "100%", background: GOLD, boxShadow: `0 0 12px ${GOLD}`}} /></div>
        {steps.map((t, i) => <div key={i} style={{position: "absolute", top: 172, left: 80 + i * ((W - 160) / steps.length), fontFamily: TYPE, fontSize: 26,
          color: prog >= i / steps.length ? GOLD : MUTED}}>{`0${i + 1}  ${t.toUpperCase()}`}</div>)}
      </>}
      <svg width={W} height={H} style={{position: "absolute"}}>
        {xs.slice(1).map((x, i) => <line key={i} x1={xs[i] + 110} y1={y} x2={x - 110} y2={y} stroke="#5a4a3a" strokeWidth={4} strokeDasharray="14 10" />)}
        {branch && <Thread x1={bx} y1={y} x2={bx} y2={by - 110} p={sp} sag={0} />}
        {f >= s(FLOW_T.go) && f < s(tAll) && pk(px, y, GOLD)}
        {branch && sp > 0 && pk(bx, y + (by - 150 - y) * sp, RED)}
      </svg>
      {nodes.map((nd, i) => (
        <div key={i} style={{position: "absolute", left: xs[i] - 120, top: y - 110, width: 240, textAlign: "center"}}>
          <Pop at={FLOW_T.node(i)}><div style={{width: 170, height: 170, margin: "0 auto", borderRadius: 18, background: "#1f1914", border: `3px solid ${GOLD}`,
            display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 18px 40px rgba(0,0,0,0.6)"}}><Icon name={nd.icon} size={100} /></div>
            <div style={{fontFamily: TYPE, fontSize: 30, color: IVORY, marginTop: 16}}>{nd.label}</div></Pop>
        </div>))}
      {branch && <div style={{position: "absolute", left: bx - 120, top: by - 110, width: 240, textAlign: "center"}}>
        <Pop at={bt + 0.5}><div style={{width: 170, height: 170, margin: "0 auto", borderRadius: 18, background: "#2a1212", border: `3px solid ${RED}`,
          display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 0 50px ${RED}66`}}><Icon name={branch.icon} size={100} /></div>
          <div style={{fontFamily: TYPE, fontSize: 30, color: IVORY, marginTop: 16}}>{branch.label}</div></Pop></div>}
      {branch && <div style={{position: "absolute", left: bx + 140, top: by - 60}}><Big at={bt + 0.7} text={branch.text} color={RED} size={70} /></div>}
    </Desk>
  );
};

/* ======================= FLIP: Akte dreht sich um -> Enthuellung ======================= */
export type FlipProps = {teaser?: string; front: {title: string; icon?: string}; back: {title: string; sub?: string}; at?: number};
export const FLIP_T = {teaser: 0.25, glitch: (at: number) => at - 0.6, flip: (at: number) => at};
export const FlipC: React.FC<FlipProps> = ({teaser, front, back, at = 2.4}) => {
  const f = useCurrentFrame();
  const fl = interpolate(f, [s(at), s(at + 0.3)], [0, 180], {...clamp, easing: Easing.bezier(0.7, 0, 0.3, 1)});
  const tease = interpolate(f, [s(0.2), s(at - 0.1)], [0, 24], {...clamp, easing: Easing.inOut(Easing.sin)});
  const shake = f >= s(at + 0.15) && f < s(at + 0.55) ? (random(`sh${f}`) - 0.5) * 26 : 0;
  return (
    <Desk red={fl > 90}>
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", transform: `translate(${shake}px,${shake * 0.5}px)`}}>
        <div style={{perspective: 2000}}>
          <div style={{width: 620, height: 760, position: "relative", transformStyle: "preserve-3d", transform: `rotateY(${fl > 0 ? fl : tease}deg)`}}>
            <div style={{position: "absolute", inset: 0, backfaceVisibility: "hidden", background: IVORY, boxShadow: "0 30px 80px rgba(0,0,0,0.7)",
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 36}}>
              <div style={{position: "absolute", top: 34, left: 40, fontFamily: TYPE, fontSize: 26, color: INK}}>FILE No. 0047 — CONFIDENTIAL</div>
              <Glitch at={FLIP_T.glitch(at)}><Icon name={front.icon || "doc"} size={220} color={INK} /></Glitch>
              <div style={{fontFamily: ANTON, fontSize: 96, color: INK, textAlign: "center", lineHeight: 1}}>{front.title}</div>
            </div>
            <div style={{position: "absolute", inset: 0, backfaceVisibility: "hidden", transform: "rotateY(180deg)", background: "#2a0c0c", border: `4px solid ${RED}`,
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 22, boxShadow: `0 0 120px ${RED}88`}}>
              <div style={{fontFamily: ANTON, fontSize: back.title.length > 8 ? 120 : 200, color: IVORY, lineHeight: 1, textAlign: "center"}}>{back.title}</div>
              <div style={{width: 320, height: 5, background: RED}} />
              {back.sub && <div style={{fontFamily: TYPE, fontSize: 34, color: IVORY, textAlign: "center", padding: "0 30px"}}>{back.sub}</div>}
            </div>
          </div>
        </div>
      </AbsoluteFill>
      {teaser && <div style={{position: "absolute", left: 90, bottom: 90}}><Typed text={teaser} at={FLIP_T.teaser} style={{fontSize: 44, color: MUTED}} cursor={f < s(at)} /></div>}
    </Desk>
  );
};

/* ======================= COUNTER: grosse Zahl, dahinter fliegen Geldscheine / Nachrichten / Akten ======================= */
export type CounterProps = {label?: string; value: number; prefix?: string; suffix?: string; dec?: number; caption: string; items?: "money" | "messages" | "docs" | "none"};
export const COUNTER_T = {start: 0.1, dur: 1.6, caption: 0.9};
export const CounterC: React.FC<CounterProps> = ({label, value, prefix, suffix, dec, caption, items = "money"}) => {
  const f = useCurrentFrame();
  return (
    <Desk>
      {items !== "none" && Array.from({length: 40}).map((_, i) => {
        const x = random(`mx${i}`) * 1840; const v = 5 + random(`ms${i}`) * 9; const y = 1150 - ((f * v + random(`my${i}`) * 1400) % 1400);
        const rot = (random(`r${i}`) - 0.5) * 50 + f * (random(`rr${i}`) - 0.5) * 0.6;
        const st: React.CSSProperties = items === "money" ? {width: 170, height: 78, background: "#4f6b43", border: `3px solid #8fa77a`}
          : items === "docs" ? {width: 110, height: 140, background: IVORY} : {width: 160 + random(`w${i}`) * 120, height: 42, borderRadius: 21, background: i % 3 ? "#2c241d" : "#5a4320"};
        return <div key={i} style={{position: "absolute", left: x, top: y, opacity: 0.35, transform: `rotate(${rot}deg)`, ...st}} />;
      })}
      <Label text={label} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        <div style={{background: "rgba(14,11,9,0.85)", padding: "26px 70px", textAlign: "center", borderTop: `6px solid ${RED}`}}>
          <div style={{fontFamily: ANTON, fontSize: 210, color: IVORY, lineHeight: 1}}><Counter to={value} at={COUNTER_T.start} dur={COUNTER_T.dur} prefix={prefix} suffix={suffix} dec={dec} /></div>
          <Pop at={COUNTER_T.caption}><div style={{fontFamily: TYPE, fontSize: 48, color: GOLD, letterSpacing: 4, marginTop: 6}}>{caption}</div></Pop>
        </div>
      </AbsoluteFill>
    </Desk>
  );
};

/* ======================= GRID: viele Akten-Kaertchen fuellen sich + Zahl ======================= */
export type GridProps = {label?: string; n?: number; icon?: string; value: number; suffix?: string; caption: string; hot?: number};
export const GRID_T = {fill: [0.15, 1.45], counter: 0.9, caption: 1.6};
export const GridC: React.FC<GridProps> = ({label, n = 60, icon = "person", value, suffix = "", caption, hot = 9}) => {
  const f = useCurrentFrame();
  return (
    <Desk>
      <Label text={label} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", flexDirection: "row", gap: 90}}>
        <div style={{display: "grid", gridTemplateColumns: "repeat(10, 66px)", gap: 14}}>
          {Array.from({length: n}).map((_, i) => {
            const at = s(GRID_T.fill[0] + random(`o${i}`) * (GRID_T.fill[1] - GRID_T.fill[0]));
            const p = interpolate(f, [at, at + 7], [0, 1], {...clamp, easing: ease}); const h = hot > 0 && i % hot === 3;
            return <div key={i} style={{width: 66, height: 66, background: h ? "#3a1212" : IVORY, transform: `scale(${p}) rotate(${(random(`q${i}`) - 0.5) * 6}deg)`, opacity: p,
              display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 10px rgba(0,0,0,0.5)", border: h ? `3px solid ${RED}` : "none"}}>
              <Icon name={icon} size={50} color={h ? RED : INK} /></div>;
          })}
        </div>
        <div>
          <div style={{fontFamily: ANTON, fontSize: (fmt(value) + suffix).length > 4 ? 170 : 220, color: IVORY, lineHeight: 1.05}}><Counter to={value} at={GRID_T.counter} dur={1.0} suffix={suffix} /></div>
          <Pop at={GRID_T.caption}><div style={{fontFamily: TYPE, fontSize: 44, color: GOLD, maxWidth: 560, marginTop: 18}}>{caption}</div></Pop>
        </div>
      </AbsoluteFill>
    </Desk>
  );
};

/* ======================= PHONE: Handy mit Chat / Mitteilungen + getipptes Zitat ======================= */
export type PhoneProps = {label?: string; app?: string; messages: [string, boolean][]; quote?: string};
export const PHONE_T = {msg: (i: number) => 0.15 + i * 0.4, quote: (n: number) => 0.15 + n * 0.4};
export const PhoneC: React.FC<PhoneProps & {len: number}> = ({label, app = "MESSAGES", messages, quote, len}) => {
  const f = useCurrentFrame(); const tilt = interpolate(f, [0, s(len)], [-16, -4], clamp);
  return (
    <Desk>
      <Label text={label} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", flexDirection: "row", gap: 110}}>
        <div style={{perspective: 1600}}>
          <div style={{width: 430, height: 860, borderRadius: 60, background: "linear-gradient(145deg,#2d2924,#0d0b09)", padding: 14, transform: `rotateY(${tilt}deg)`,
            boxShadow: "0 40px 120px rgba(0,0,0,0.85), inset 0 0 0 2px #4a4238"}}>
            <div style={{width: "100%", height: "100%", borderRadius: 48, background: "#0b0a09", overflow: "hidden", position: "relative"}}>
              <div style={{padding: "64px 28px 18px", fontFamily: SANS, fontWeight: 800, fontSize: 28, color: IVORY, borderBottom: "1px solid #2a2520"}}>{app}</div>
              <div style={{display: "flex", flexDirection: "column", gap: 16, padding: "26px 22px"}}>
                {messages.map(([t, me], i) => {
                  const sp = useSpring(PHONE_T.msg(i));
                  if (f < s(PHONE_T.msg(i))) return <div key={i} />;
                  return <div key={i} style={{alignSelf: me ? "flex-end" : "flex-start", maxWidth: 300, padding: "14px 20px", borderRadius: 22, fontFamily: SANS, fontSize: 24,
                    background: me ? "#6b4a14" : "#26211c", color: IVORY, transform: `translateY(${(1 - sp) * 26}px)`, opacity: Math.min(1, sp * 2)}}>{t}</div>;
                })}
              </div>
            </div>
          </div>
        </div>
        {quote && <div style={{width: 760}}><Typed text={`"${quote}"`} at={PHONE_T.quote(messages.length)} style={{fontSize: 60, color: IVORY, lineHeight: 1.2}} /></div>}
      </AbsoluteFill>
    </Desk>
  );
};

/* ======================= CIPHER: Text verschluesselt sich ======================= */
export type CipherProps = {label?: string; text: string; caption?: string};
export const CIPHER_T = {start: 0.3, per: 0.025, caption: 0.9};
export const CipherC: React.FC<CipherProps> = ({label, text, caption}) => {
  const f = useCurrentFrame(); const gl = "A7#Q$9X%K2@M&Z5!F8";
  const size = Math.min(70, Math.floor(1700 / Math.max(10, text.length) / 0.62));
  return (
    <Desk>
      <Label text={label} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", gap: 50}}>
        <div style={{display: "flex", justifyContent: "center"}}>
          {text.split("").map((c, i) => {
            const scr = f > s(CIPHER_T.start + i * CIPHER_T.per);
            const ch = c === " " ? " " : scr ? gl[Math.floor(random(`c${i}${Math.floor(f / 2)}`) * gl.length)] : c;
            return <span key={i} style={{fontFamily: TYPE, fontSize: size, color: scr ? RED : IVORY, width: size * 0.62, textAlign: "center", textShadow: scr ? `0 0 14px ${RED}` : "none"}}>{ch}</span>;
          })}
        </div>
        {caption && <Pop at={CIPHER_T.caption}><div style={{fontFamily: ANTON, fontSize: 64, color: IVORY, letterSpacing: 2}}>{caption}</div></Pop>}
      </AbsoluteFill>
    </Desk>
  );
};

/* ======================= STACK: Akten/Verfahren stapeln sich, Symbol knallt drauf, Frage tippt ======================= */
export type StackProps = {label?: string; cards: [string, string][]; symbol?: string; question?: string};
export const STACK_T = {card: (i: number) => 0.1 + i * 0.16, symbol: 1.5, question: 0.6};
export const StackC: React.FC<StackProps> = ({label, cards, symbol = "§", question}) => {
  const f = useCurrentFrame(); const m = (cards.length - 1) / 2;
  const hy = interpolate(f, [s(STACK_T.symbol), s(STACK_T.symbol + 0.22), s(STACK_T.symbol + 0.4)], [-60, 10, 0], {...clamp, easing: ease});
  return (
    <Desk>
      <Label text={label} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        {cards.map(([t, sub], i) => {
          const sp = useSpring(STACK_T.card(i));
          return <div key={i} style={{position: "absolute", width: 560, height: 320, background: IVORY, boxShadow: "0 20px 60px rgba(0,0,0,0.7)", padding: 32,
            transform: `translate(${(i - m) * 48}px, ${(i - m) * -30 + (1 - sp) * 700}px) rotate(${(i - m) * 4}deg)`}}>
            <div style={{fontFamily: ANTON, fontSize: 40, color: INK}}>{t}</div>
            <div style={{fontFamily: TYPE, fontSize: 26, color: "#4a4038", marginTop: 8}}>{sub}</div>
            <div style={{marginTop: 26, height: 10, width: 420, background: "#d8cfbb"}} /><div style={{marginTop: 12, height: 10, width: 340, background: "#d8cfbb"}} />
          </div>;
        })}
        <div style={{position: "absolute", top: 110, fontFamily: ANTON, fontSize: 210, color: RED, transform: `translateY(${hy}px)`, opacity: f >= s(STACK_T.symbol) ? 1 : 0,
          textShadow: "0 10px 40px #000"}}>{symbol}</div>
      </AbsoluteFill>
      {question && <div style={{position: "absolute", left: 0, right: 0, bottom: 80, textAlign: "center"}}><Typed text={question} at={STACK_T.question} style={{fontSize: 48, color: IVORY}} /></div>}
    </Desk>
  );
};
