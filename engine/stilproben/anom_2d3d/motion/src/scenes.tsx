import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame, random, Easing} from "remotion";
import {s, clamp, ease, easeIn, AMBER, RED, INK, MUTED, FONT, Backdrop, Typed, Counter, Pop, Tag, Headline, Glitch, useT, useSpring, fmt} from "./lib";
import {WorldMap, allIds} from "./map";

/* ---------- Bausteine ---------- */
const Phone: React.FC<{children: React.ReactNode; tilt?: number; scale?: number; glow?: string}> = ({children, tilt = 0, scale = 1, glow = AMBER}) => (
  <div style={{perspective: 1600}}>
    <div style={{width: 420, height: 860, borderRadius: 64, background: "linear-gradient(145deg,#2a2e36,#0c0e12)", padding: 14,
      transform: `rotateY(${tilt}deg) rotateX(${tilt * 0.25}deg) scale(${scale})`, boxShadow: `0 40px 120px rgba(0,0,0,0.8), 0 0 80px ${glow}22, inset 0 0 0 2px #3a3f49`}}>
      <div style={{width: "100%", height: "100%", borderRadius: 52, background: "#07090d", overflow: "hidden", position: "relative"}}>
        <div style={{position: "absolute", top: 16, left: "50%", marginLeft: -55, width: 110, height: 30, borderRadius: 20, background: "#000", zIndex: 5}} />
        {children}
      </div>
    </div>
  </div>
);
const LockIcon: React.FC<{size?: number; color?: string; open?: number}> = ({size = 64, color = AMBER, open = 0}) => (
  <div style={{width: size, height: size, borderRadius: size * 0.24, background: color, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 0 ${size / 2}px ${color}66`}}>
    <svg width={size * 0.5} height={size * 0.6} viewBox="0 0 40 48">
      <path d={`M10 22 V14 a10 10 0 0 1 20 0 V${22 - open * 10}`} fill="none" stroke="#1a1206" strokeWidth={5} transform={`translate(${open * 8},${-open * 4})`} />
      <rect x={4} y={22} width={32} height={24} rx={4} fill="#1a1206" />
    </svg>
  </div>
);
const Bubble: React.FC<{text: string; me?: boolean; at: number}> = ({text, me, at}) => {
  const sp = useSpring(at); const f = useCurrentFrame();
  if (f < s(at)) return null;
  return <div style={{alignSelf: me ? "flex-end" : "flex-start", maxWidth: 300, padding: "14px 20px", borderRadius: 24, fontFamily: FONT, fontWeight: 500, fontSize: 24,
    background: me ? "#7a4e0e" : "#20242e", color: INK, transform: `translateY(${(1 - sp) * 30}px) scale(${0.85 + sp * 0.15})`, opacity: Math.min(1, sp * 2),
    transformOrigin: me ? "right bottom" : "left bottom"}}>{text}</div>;
};

/* ---------- Overlay fuer den 3D-Hook ---------- */
export const HookOverlay: React.FC = () => {
  const k = useSpring(3.1);
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", left: 90, bottom: 110}}>
        <Typed text="JUNI 2021" at={0.35} cps={12} style={{fontWeight: 800, fontSize: 54, letterSpacing: 6, color: INK, textShadow: "0 4px 20px #000"}} />
        <div style={{height: 4, width: interpolate(f, [s(0.4), s(1.4)], [0, 260], {...clamp, easing: ease}), background: AMBER, marginTop: 12}} />
      </div>
      {f >= s(3.1) && <div style={{position: "absolute", right: 110, top: 130, textAlign: "right", transform: `scale(${0.7 + 0.3 * k})`, opacity: Math.min(1, k * 1.5), transformOrigin: "right top"}}>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 150, color: INK, lineHeight: 1, textShadow: "0 10px 40px #000"}}><Counter to={12000} at={3.1} dur={0.9} /></div>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 40, letterSpacing: 8, color: AMBER}}>ANOM-HANDYS</div>
      </div>}
    </AbsoluteFill>
  );
};

/* ---------- B: Karte, Handys verteilen sich, Banden vernetzen sich ---------- */
export const SwarmMap: React.FC = () => (
  <Backdrop tint="#101624">
    <WorldMap swarm={{at: 0.0, dur: 1.4, n: 260}} links={{at: 0.5, n: 26}} zoom={[0, 2.4, 1.08, 1.0]} />
    <AbsoluteFill style={{justifyContent: "flex-end", alignItems: "center", paddingBottom: 90}}>
      <Pop at={0.4}><div style={{fontFamily: FONT, fontWeight: 900, fontSize: 64, color: INK, letterSpacing: 2, background: "rgba(10,12,18,0.8)", padding: "10px 30px", borderLeft: `8px solid ${AMBER}`}}>HUNDERTE BANDEN</div></Pop>
    </AbsoluteFill>
  </Backdrop>
);

/* ---------- C: Chat, "Hier liest niemand mit" ---------- */
export const ChatScene: React.FC = () => {
  const tilt = interpolate(useCurrentFrame(), [0, s(2.7)], [-18, -6], clamp);
  return (
    <Backdrop tint="#1a1408">
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", flexDirection: "row", gap: 120}}>
        <Phone tilt={tilt}>
          <div style={{padding: "70px 26px 0", display: "flex", alignItems: "center", gap: 16}}>
            <LockIcon size={56} />
            <div><div style={{fontFamily: FONT, fontWeight: 900, fontSize: 30, color: INK}}>ANOM</div>
              <div style={{fontFamily: FONT, fontSize: 16, color: AMBER}}>Ende-zu-Ende verschlüsselt</div></div>
          </div>
          <div style={{display: "flex", flexDirection: "column", gap: 16, padding: "36px 22px"}}>
            <Bubble text="Ware ist da." at={0.1} />
            <Bubble text="Gut. Treffpunkt wie immer." me at={0.45} />
            <Bubble text="Sicher, dass das hier sicher ist?" at={0.85} />
            <Bubble text="Hier liest niemand mit." me at={1.15} />
          </div>
        </Phone>
        <div style={{width: 760}}>
          <Typed text="„Hier liest niemand mit.“" at={1.1} cps={22} style={{fontWeight: 800, fontSize: 64, color: INK, lineHeight: 1.15}} />
        </div>
      </AbsoluteFill>
    </Backdrop>
  );
};

/* ---------- D: App-Reveal ANOM ---------- */
export const AppReveal: React.FC = () => {
  const f = useCurrentFrame();
  const sp = useSpring(0.0, {damping: 11, mass: 0.7, stiffness: 120});
  const letters = "ANOM".split("");
  return (
    <Backdrop tint="#1c1609">
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", gap: 40}}>
        <div style={{transform: `scale(${sp}) rotate(${(1 - sp) * -25}deg)`}}><LockIcon size={220} /></div>
        <div style={{display: "flex", gap: 10}}>
          {letters.map((l, i) => {
            const p = interpolate(f, [s(0.75 + i * 0.07), s(0.95 + i * 0.07)], [0, 1], {...clamp, easing: ease});
            const ch = p < 1 && p > 0 ? "X#@$%&"[Math.floor(random(`${f}${i}`) * 6)] : l;
            return <span key={i} style={{fontFamily: FONT, fontWeight: 900, fontSize: 150, color: INK, letterSpacing: 18, opacity: p, transform: `translateY(${(1 - p) * 30}px)`}}>{p > 0 ? ch : ""}</span>;
          })}
        </div>
        <Pop at={1.2}><div style={{fontFamily: FONT, fontSize: 30, letterSpacing: 10, color: AMBER, fontWeight: 700}}>DIE „SICHERE“ APP</div></Pop>
      </AbsoluteFill>
    </Backdrop>
  );
};

/* ---------- E: Spezialhandy mit nur einer Aufgabe ---------- */
export const OneApp: React.FC = () => {
  const f = useCurrentFrame();
  const apps = ["Kamera", "Browser", "Karten", "Telefon", "Mail", "Fotos", "Musik", "Store"];
  const tilt = interpolate(f, [0, s(2.6)], [16, 4], clamp);
  return (
    <Backdrop tint="#121826">
      <Tag text="SPEZIALHANDY" />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", transform: "translateX(-300px)"}}>
        <Phone tilt={tilt}>
          <div style={{display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 26, padding: "110px 34px 0"}}>
            {apps.map((a, i) => {
              const x = interpolate(f, [s(0.5 + i * 0.1), s(0.75 + i * 0.1)], [0, 1], {...clamp, easing: ease});
              return <div key={a} style={{display: "flex", flexDirection: "column", alignItems: "center", gap: 8, opacity: 1 - x * 0.75}}>
                <div style={{width: 92, height: 92, borderRadius: 24, background: "#252a35", position: "relative"}}>
                  <svg width={92} height={92} style={{position: "absolute"}}><line x1={18} y1={18} x2={18 + 56 * x} y2={18 + 56 * x} stroke={RED} strokeWidth={7} strokeLinecap="round" /><line x1={74} y1={18} x2={74 - 56 * x} y2={18 + 56 * x} stroke={RED} strokeWidth={7} strokeLinecap="round" /></svg>
                </div>
                <div style={{fontFamily: FONT, fontSize: 17, color: MUTED}}>{a}</div>
              </div>;
            })}
            <Pop at={1.6} style={{display: "flex", flexDirection: "column", alignItems: "center", gap: 8}}>
              <LockIcon size={92} /><div style={{fontFamily: FONT, fontSize: 17, color: AMBER, fontWeight: 700}}>ANOM</div>
            </Pop>
          </div>
        </Phone>
      </AbsoluteFill>
      <div style={{position: "absolute", left: 1050, top: 400}}><Headline at={1.7} lines={["1 APP.", "SONST NICHTS."]} accent={0} size={90} /></div>
    </Backdrop>
  );
};

/* ---------- F: Verschluesselung ---------- */
export const Cipher: React.FC = () => {
  const f = useCurrentFrame();
  const msg = "TREFFEN FREITAG 23 UHR HAFEN";
  const glyph = "A7#Q$9X%K2@M&Z5!F8";
  return (
    <Backdrop tint="#0f1a1c">
      <Tag text="VERSCHLÜSSELT" />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", gap: 50}}>
        <div style={{display: "flex", gap: 4, justifyContent: "center", width: 1800}}>
          {msg.split("").map((c, i) => {
            const at = s(0.3 + i * 0.025);
            const scr = f > at;
            const ch = c === " " ? " " : scr ? glyph[Math.floor(random(`c${i}${Math.floor(f / 2)}`) * glyph.length)] : c;
            return <span key={i} style={{fontFamily: "DejaVu Sans Mono, monospace", fontWeight: 700, fontSize: 64, color: scr ? AMBER : INK, textShadow: scr ? `0 0 18px ${AMBER}` : "none", width: 46, textAlign: "center"}}>{ch}</span>;
          })}
        </div>
        <Pop at={0.9}><div style={{display: "flex", alignItems: "center", gap: 20}}><LockIcon size={70} /><div style={{fontFamily: FONT, fontWeight: 800, fontSize: 44, color: INK, letterSpacing: 3}}>FÜR AUSSENSTEHENDE UNLESBAR</div></div></Pop>
      </AbsoluteFill>
    </Backdrop>
  );
};

/* ---------- G: Fernloeschung ---------- */
export const Wipe: React.FC = () => {
  const f = useCurrentFrame();
  const press = useSpring(0.75, {damping: 9, mass: 0.4, stiffness: 300});
  const wipeP = interpolate(f, [s(0.95), s(1.8)], [0, 1], {...clamp, easing: ease});
  const cursor = interpolate(f, [0, s(0.7)], [0, 1], {...clamp, easing: ease});
  return (
    <Backdrop tint="#1d0c0c">
      <Tag text="FERNLÖSCHUNG" color={RED} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        <Phone tilt={-6} glow={RED}>
          <div style={{display: "flex", flexDirection: "column", gap: 16, padding: "110px 22px", filter: `blur(${wipeP * 6}px)`, opacity: 1 - wipeP}}>
            {["Ware ist da.", "Treffpunkt wie immer.", "Wie viele?", "Wie besprochen.", "Zahlung morgen."].map((t, i) => (
              <div key={i} style={{alignSelf: i % 2 ? "flex-end" : "flex-start", padding: "14px 20px", borderRadius: 24, background: i % 2 ? "#7a4e0e" : "#20242e", color: INK, fontFamily: FONT, fontSize: 24,
                transform: `translateX(${wipeP * (i % 2 ? 300 : -300) * (0.6 + i * 0.1)}px)`}}>{t}</div>
            ))}
          </div>
          {wipeP > 0.6 && <AbsoluteFill style={{alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 14}}>
            <svg width={120} height={120}><circle cx={60} cy={60} r={50} stroke={RED} strokeWidth={8} fill="none" strokeDasharray={314} strokeDashoffset={314 * (1 - (wipeP - 0.6) / 0.4)} transform="rotate(-90 60 60)" /></svg>
            <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 30, color: INK}}>ALLES GELÖSCHT</div>
          </AbsoluteFill>}
          <div style={{position: "absolute", bottom: 46, left: "50%", marginLeft: -110, width: 220, height: 84, borderRadius: 42, background: RED, display: "flex", alignItems: "center", justifyContent: "center",
            transform: `scale(${1 - 0.12 * Math.sin(Math.min(1, press) * Math.PI)})`, boxShadow: `0 0 ${30 + press * 40}px ${RED}`}}>
            <span style={{fontFamily: FONT, fontWeight: 900, fontSize: 34, color: "#fff", letterSpacing: 4}}>WIPE</span>
          </div>
        </Phone>
        <svg width={70} height={70} style={{position: "absolute", left: 960 + 260 - cursor * 250, top: 980 - cursor * 70}} viewBox="0 0 24 24">
          <path d="M5 3l14 8-6 2 4 7-3 1-4-7-5 4z" fill="#fff" stroke="#000" strokeWidth={1} />
        </svg>
      </AbsoluteFill>
    </Backdrop>
  );
};

/* ---------- H: 300+ Organisationen ---------- */
export const Orgs: React.FC = () => {
  const f = useCurrentFrame();
  const N = 60;
  return (
    <Backdrop tint="#14121c">
      <Tag text="DIE KUNDEN" />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", flexDirection: "row", gap: 90}}>
        <div style={{display: "grid", gridTemplateColumns: "repeat(10, 64px)", gap: 14}}>
          {Array.from({length: N}).map((_, i) => {
            const at = s(0.15 + random(`o${i}`) * 1.3);
            const p = interpolate(f, [at, at + 7], [0, 1], {...clamp, easing: ease});
            const hot = i % 11 === 3;
            return <div key={i} style={{width: 64, height: 64, borderRadius: 16, background: hot ? "#3a1414" : "#1d2230", border: `2px solid ${hot ? RED : "#30384a"}`, transform: `scale(${p})`, opacity: p,
              display: "flex", alignItems: "flex-end", justifyContent: "center", overflow: "hidden"}}>
              <svg width={40} height={46} viewBox="0 0 40 46"><circle cx={20} cy={15} r={10} fill={hot ? RED : "#59637a"} /><path d="M2 46c0-12 8-20 18-20s18 8 18 20z" fill={hot ? RED : "#59637a"} /></svg>
            </div>;
          })}
        </div>
        <div>
          <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 210, color: INK, lineHeight: 0.9}}><Counter to={300} at={0.9} dur={1.0} suffix="+" /></div>
          <Pop at={1.6}><div style={{fontFamily: FONT, fontWeight: 800, fontSize: 40, letterSpacing: 4, color: AMBER, marginTop: 10}}>KRIMINELLE<br />ORGANISATIONEN</div></Pop>
        </div>
      </AbsoluteFill>
    </Backdrop>
  );
};

/* ---------- I: 100+ Laender ---------- */
const hundred = allIds.filter((id, i) => random(`h${id}`) < 0.62).slice(0, 110);
export const Countries: React.FC = () => (
  <Backdrop tint="#101624">
    <WorldMap highlight={hundred.map((id, i) => ({id, at: 0.05 + (i / hundred.length) * 1.0}))} zoom={[0, 1.7, 1.0, 1.05]} />
    <AbsoluteFill style={{justifyContent: "flex-end", alignItems: "center", paddingBottom: 80}}>
      <div style={{display: "flex", alignItems: "baseline", gap: 24, background: "rgba(10,12,18,0.85)", padding: "10px 36px", borderLeft: `8px solid ${AMBER}`}}>
        <span style={{fontFamily: FONT, fontWeight: 900, fontSize: 96, color: INK}}><Counter to={100} at={0.1} dur={1.0} suffix="+" /></span>
        <span style={{fontFamily: FONT, fontWeight: 800, fontSize: 44, color: AMBER, letterSpacing: 4}}>LÄNDER</span>
      </div>
    </AbsoluteFill>
  </Backdrop>
);

/* ---------- K: Neugier-Pause + Enthuellung FBI ---------- */
export const Reveal: React.FC = () => {
  const f = useCurrentFrame();
  // 0..0.7 Stille, Karte dreht sich langsam halb, 2.0 Glitch, 4.1 Flip auf FBI
  const flip = interpolate(f, [s(4.05), s(4.35)], [0, 180], {...clamp, easing: Easing.bezier(0.7, 0, 0.3, 1)});
  const tease = interpolate(f, [s(0.2), s(3.8)], [0, 28], {...clamp, easing: Easing.inOut(Easing.sin)});
  const shake = f >= s(4.2) && f < s(4.6) ? (random(`sh${f}`) - 0.5) * 24 : 0;
  const light = interpolate(f, [0, s(0.7), s(4.15), s(4.4)], [0.25, 0.6, 0.6, 1], clamp);
  return (
    <Backdrop tint={flip > 90 ? "#2a0d0d" : "#131722"}>
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", transform: `translate(${shake}px, ${shake * 0.5}px)`, opacity: light}}>
        <div style={{perspective: 2000}}>
          <div style={{width: 560, height: 700, position: "relative", transformStyle: "preserve-3d", transform: `rotateY(${(flip > 0 ? flip : tease)}deg)`}}>
            <div style={{position: "absolute", inset: 0, backfaceVisibility: "hidden", borderRadius: 40, background: "linear-gradient(160deg,#1f2430,#0f1218)", border: "2px solid #343b4b",
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40}}>
              <Glitch at={2.0} dur={0.4}><LockIcon size={200} /></Glitch>
              <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 96, color: INK, letterSpacing: 14}}>ANOM</div>
            </div>
            <div style={{position: "absolute", inset: 0, backfaceVisibility: "hidden", transform: "rotateY(180deg)", borderRadius: 40, background: "linear-gradient(160deg,#3a0f0f,#140606)", border: `3px solid ${RED}`,
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 18, boxShadow: `0 0 120px ${RED}88`}}>
              <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 230, color: "#fff", letterSpacing: 10, lineHeight: 1}}>FBI</div>
              <div style={{width: 300, height: 4, background: RED}} />
              <div style={{fontFamily: FONT, fontWeight: 700, fontSize: 30, color: INK, letterSpacing: 6}}>BETREIBER DER APP</div>
            </div>
          </div>
        </div>
      </AbsoluteFill>
      <div style={{position: "absolute", left: 90, bottom: 90}}>
        <Typed text="Was die Käufer nicht wissen …" at={0.25} cps={20} style={{fontWeight: 700, fontSize: 40, color: MUTED}} cursor={f < s(4.0)} />
      </div>
    </Backdrop>
  );
};

/* ---------- L: Kopie jeder Nachricht ---------- */
export const CopyFlow: React.FC = () => {
  const f = useCurrentFrame();
  const A = {x: 360, y: 520}, B = {x: 1560, y: 520}, C = {x: 960, y: 880};
  const go = interpolate(f, [s(0.4), s(1.9)], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const split = interpolate(f, [s(1.6), s(2.8)], [0, 1], {...clamp, easing: ease});
  const prog = interpolate(f, [0, s(3.2)], [0, 1], clamp);
  const node = (p: {x: number; y: number}, label: string, col: string, icon: React.ReactNode, at: number) => (
    <div style={{position: "absolute", left: p.x - 110, top: p.y - 110, width: 220, textAlign: "center"}}>
      <Pop at={at}><div style={{width: 160, height: 160, margin: "0 auto", borderRadius: 40, background: "#1b202b", border: `3px solid ${col}`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 0 40px ${col}44`}}>{icon}</div>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 28, color: INK, marginTop: 14, letterSpacing: 2}}>{label}</div></Pop>
    </div>
  );
  const phoneIcon = <svg width={70} height={100} viewBox="0 0 70 100"><rect x={4} y={2} width={62} height={96} rx={12} fill="none" stroke={INK} strokeWidth={6} /><circle cx={35} cy={86} r={4} fill={INK} /></svg>;
  const srv = <svg width={90} height={90} viewBox="0 0 90 90">{[8, 36, 64].map((y) => <g key={y}><rect x={6} y={y} width={78} height={20} rx={4} fill="none" stroke={RED} strokeWidth={5} /><circle cx={70} cy={y + 10} r={4} fill={RED} /></g>)}</svg>;
  const env = (x: number, y: number, col: string, o = 1) => (
    <g transform={`translate(${x - 34},${y - 24})`} opacity={o}><rect width={68} height={48} rx={6} fill={col} /><path d="M2 4 L34 28 L66 4" fill="none" stroke="#111" strokeWidth={4} /></g>
  );
  const ex = A.x + (B.x - A.x) * go;
  const mid = {x: (A.x + B.x) / 2, y: A.y};
  const cx = mid.x + (C.x - mid.x) * split, cy = mid.y + (C.y - 80 - mid.y) * split;
  return (
    <Backdrop tint="#151820">
      <Tag text="SO FUNKTIONIERT DER TRICK" />
      <div style={{position: "absolute", left: 70, right: 70, top: 120, height: 6, background: "#232a38", borderRadius: 3}}>
        <div style={{width: `${prog * 100}%`, height: "100%", background: AMBER, borderRadius: 3, boxShadow: `0 0 12px ${AMBER}`}} />
      </div>
      {["SENDEN", "KOPIEREN", "MITLESEN"].map((t, i) => <div key={t} style={{position: "absolute", top: 140, left: 70 + i * 600, fontFamily: FONT, fontSize: 20, fontWeight: 700, letterSpacing: 3, color: prog > i / 3 ? AMBER : MUTED}}>{`0${i + 1}  ${t}`}</div>)}
      <svg width={1920} height={1080} style={{position: "absolute"}}>
        <line x1={A.x + 100} y1={A.y - 40} x2={B.x - 100} y2={B.y - 40} stroke="#3a4356" strokeWidth={4} strokeDasharray="14 10" />
        <path d={`M${mid.x},${mid.y - 40} L${mid.x},${C.y - 120}`} stroke={RED} strokeWidth={4} strokeDasharray="14 10" opacity={split} />
        {go > 0 && go < 1 && env(ex, A.y - 40, AMBER)}
        {go >= 1 && env(B.x - 100, B.y - 40, AMBER, interpolate(f, [s(1.9), s(2.3)], [1, 0], clamp))}
        {split > 0 && env(cx, cy - 40 + 40 * split, RED)}
      </svg>
      {node(A, "KRIMINELLER A", AMBER, phoneIcon, 0.05)}
      {node(B, "KRIMINELLER B", AMBER, phoneIcon, 0.15)}
      {node(C, "ERMITTLER", RED, srv, 1.7)}
      {split > 0.3 && <div style={{position: "absolute", left: 1020, top: 690, fontFamily: FONT, fontWeight: 900, fontSize: 44, color: RED, letterSpacing: 3}}>
        <Typed text="HEIMLICHE KOPIE" at={2.0} cps={26} cursor={false} /></div>}
    </Backdrop>
  );
};

/* ---------- Overlay Serverraum: 18 Monate ---------- */
export const ServerOverlay: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [s(at), s(at + 1.5)], [0, 1], {...clamp, easing: ease});
  if (f < s(at)) return null;
  return (
    <div style={{position: "absolute", left: 90, bottom: 100, width: 760}}>
      <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 96, color: INK, textShadow: "0 6px 30px #000"}}><Counter to={18} at={at} dur={1.5} /> MONATE</div>
      <div style={{height: 8, background: "rgba(255,255,255,0.15)", marginTop: 10}}><div style={{width: `${p * 100}%`, height: "100%", background: AMBER, boxShadow: `0 0 14px ${AMBER}`}} /></div>
      <div style={{display: "flex", justifyContent: "space-between", fontFamily: FONT, fontSize: 22, color: INK, marginTop: 8, fontWeight: 600}}><span>2019</span><span>MITGELESEN</span><span>2021</span></div>
    </div>
  );
};

/* ---------- N: 27 Millionen Nachrichten ---------- */
export const Messages: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Backdrop tint="#161208">
      {Array.from({length: 46}).map((_, i) => {
        const x = random(`mx${i}`) * 1840; const sp = 6 + random(`ms${i}`) * 10; const y = 1150 - ((f * sp + random(`my${i}`) * 1400) % 1400);
        const w = 120 + random(`mw${i}`) * 180;
        return <div key={i} style={{position: "absolute", left: x, top: y, width: w, height: 40, borderRadius: 20, background: i % 3 ? "#1e232e" : "#5a3a0c", opacity: 0.55}} />;
      })}
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        <div style={{background: "rgba(11,13,18,0.82)", padding: "30px 60px", borderRadius: 16, textAlign: "center"}}>
          <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 190, color: INK, lineHeight: 1}}><Counter to={27000000} at={0.0} dur={1.6} /></div>
          <Pop at={0.9}><div style={{fontFamily: FONT, fontWeight: 800, fontSize: 48, color: AMBER, letterSpacing: 8}}>NACHRICHTEN MITGELESEN</div></Pop>
        </div>
      </AbsoluteFill>
    </Backdrop>
  );
};

/* ---------- O: Viele davon auf Deutsch + Pause ---------- */
export const German: React.FC = () => {
  const f = useCurrentFrame();
  const dark = interpolate(f, [s(2.0), s(2.4)], [1, 0.12], clamp);
  return (
    <Backdrop tint="#101624">
      <WorldMap view="europe" highlight={[{id: "528", at: 0.3, color: "#6d7891"}, {id: "752", at: 0.45, color: "#6d7891"}, {id: "276", at: 1.25}]} zoom={[0, 2.8, 1.0, 1.12]} dim={dark} />
      <AbsoluteFill style={{opacity: Math.max(0, (dark - 0.12) / 0.88)}}>
        <div style={{position: "absolute", left: 1150, top: 560}}><Pop at={1.3}><div style={{fontFamily: FONT, fontWeight: 900, fontSize: 80, color: INK, background: "rgba(10,12,18,0.85)", padding: "6px 26px", borderLeft: `8px solid ${AMBER}`}}>AUF DEUTSCH</div></Pop></div>
        <div style={{position: "absolute", left: 90, bottom: 70, fontFamily: FONT, fontSize: 24, color: MUTED, fontWeight: 600}}>Häufigste Sprachen laut Ermittlern: Niederländisch, Deutsch, Schwedisch</div>
      </AbsoluteFill>
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        <Typed text="JUNI 2021" at={2.5} cps={12} style={{fontWeight: 900, fontSize: 110, color: INK, letterSpacing: 10}} />
      </AbsoluteFill>
    </Backdrop>
  );
};

/* ---------- P: Zugriff weltweit ---------- */
const RAIDS: [string, string][] = [["036", "AUSTRALIEN"], ["554", "NEUSEELAND"], ["528", ""], ["276", "DEUTSCHLAND"], ["752", "SCHWEDEN"], ["840", "USA"], ["124", ""], ["578", ""], ["246", ""], ["208", ""], ["040", ""], ["348", ""], ["233", ""], ["440", ""], ["688", ""], ["826", ""]];
export const Raids: React.FC = () => {
  const f = useCurrentFrame();
  const flash = f >= s(2.6) ? (Math.floor((f - s(2.6)) / 5) % 2 ? RED : "#2a62ff") : "transparent";
  return (
    <Backdrop tint="#1a0f12">
      <WorldMap pins={RAIDS.map(([id, label], i) => ({id, label: label || undefined, at: 1.55 + i * 0.06}))} pulseAll={2.6} zoom={[0, 4.2, 1.12, 1.0]} />
      <AbsoluteFill style={{boxShadow: `inset 0 0 220px ${flash}`, opacity: 0.55}} />
      <div style={{position: "absolute", left: 70, top: 60}}><Headline at={0.15} lines={["ZUGRIFF"]} size={110} /></div>
      <div style={{position: "absolute", right: 80, top: 70, fontFamily: "DejaVu Sans Mono, monospace", fontSize: 54, color: RED, fontWeight: 700}}>
        {""}
      </div>
    </Backdrop>
  );
};

/* ---------- Overlay Beweismittel: Bilanz ---------- */
export const EvidenceOverlay: React.FC = () => {
  const items: [number, string, string, number][] = [[800, "+", "FESTNAHMEN", 0.25], [8, " t", "KOKAIN", 2.25], [250, "", "SCHUSSWAFFEN", 3.95]];
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", right: 90, top: 140, display: "flex", flexDirection: "column", gap: 26, alignItems: "flex-end"}}>
        {items.map(([n, suf, lab, at]) => (
          <Pop key={lab} at={at} from={0.8}>
            <div style={{background: "rgba(10,12,18,0.82)", padding: "10px 30px", borderRight: `10px solid ${AMBER}`, textAlign: "right"}}>
              <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 104, color: INK, lineHeight: 1}}><Counter to={n} at={at} dur={0.7} suffix={suf} /></div>
              <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 30, color: AMBER, letterSpacing: 6}}>{lab}</div>
            </div>
          </Pop>
        ))}
      </div>
      <div style={{position: "absolute", left: 80, bottom: 60, fontFamily: FONT, fontSize: 22, color: "#c9ced8", fontWeight: 600}}>Symbolbild · Zahlen: Europol / FBI, Juni 2021</div>
    </AbsoluteFill>
  );
};

/* ---------- R: Gerichte ---------- */
export const Courts: React.FC = () => {
  const f = useCurrentFrame();
  const cards = ["VERFAHREN 1", "VERFAHREN 2", "VERFAHREN 3", "VERFAHREN 4", "VERFAHREN 5"];
  const hammer = interpolate(f, [s(1.7), s(1.95), s(2.15)], [-40, 8, 0], {...clamp, easing: ease});
  return (
    <Backdrop tint="#16131d">
      <Tag text="BIS HEUTE UMSTRITTEN" />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        {cards.map((c, i) => {
          const sp = useSpring(0.1 + i * 0.16);
          return <div key={c} style={{position: "absolute", width: 520, height: 300, borderRadius: 14, background: "#e9e5da", boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
            transform: `translate(${(i - 2) * 46}px, ${(i - 2) * -30 + (1 - sp) * 600}px) rotate(${(i - 2) * 4}deg)`, padding: 30}}>
            <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 30, color: "#222"}}>{c}</div>
            <div style={{fontFamily: FONT, fontSize: 22, color: "#555", marginTop: 10}}>Beweismittel: ANOM-Chats</div>
            <div style={{marginTop: 26, height: 10, width: 400, background: "#cfcabd"}} /><div style={{marginTop: 12, height: 10, width: 330, background: "#cfcabd"}} />
            <div style={{position: "absolute", right: 24, bottom: 18, fontFamily: FONT, fontWeight: 900, fontSize: 80, color: RED}}>?</div>
          </div>;
        })}
        <div style={{position: "absolute", top: 120, fontFamily: FONT, fontWeight: 900, fontSize: 200, color: AMBER, transform: `translateY(${hammer}px)`, textShadow: "0 10px 40px #000", opacity: f > s(1.7) ? 1 : 0}}>§</div>
      </AbsoluteFill>
      <div style={{position: "absolute", left: 0, right: 0, bottom: 80, textAlign: "center"}}>
        <Typed text="Dürfen die Chats als Beweis verwendet werden?" at={0.6} cps={28} style={{fontWeight: 800, fontSize: 46, color: INK}} />
      </div>
    </Backdrop>
  );
};

/* ---------- S: Schluss-Overlay ---------- */
export const EndOverlay: React.FC = () => {
  const f = useCurrentFrame();
  const d = interpolate(f, [s(0.0), s(0.5), s(1.8), s(2.3)], [0, 0.4, 0.4, 0.7], clamp);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: `rgba(0,0,0,${d})`}} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        <Headline at={0.15} lines={["DURFTE DAS FBI", "DAS ÜBERHAUPT?"]} accent={1} size={120} color={RED} />
      </AbsoluteFill>
      <div style={{position: "absolute", left: 0, right: 0, bottom: 70, textAlign: "center", opacity: interpolate(f, [s(3.4), s(3.9)], [0, 1], clamp)}}>
        <span style={{fontFamily: FONT, fontWeight: 700, fontSize: 28, letterSpacing: 10, color: MUTED}}>OPERATION TROJAN SHIELD · STILPROBE</span>
      </div>
    </AbsoluteFill>
  );
};
