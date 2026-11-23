import React, {useMemo} from "react";
import {AbsoluteFill, useCurrentFrame, interpolate, random} from "remotion";
import {geoNaturalEarth1, geoPath, geoCentroid, GeoProjection} from "d3-geo";
import {feature} from "topojson-client";
// @ts-ignore
import world from "world-atlas/countries-50m.json";
import {s, clamp, AMBER, RED, INK, FONT, ease, MUTED} from "./lib";

const W = 1920, H = 1080;
// @ts-ignore
const countries: any = feature(world, world.objects.countries);
const feats: any[] = countries.features.filter((d: any) => d.id !== "010"); // ohne Antarktis

export const byId = (id: string) => feats.find((d) => d.id === id);

export const makeProj = (view: "world" | "europe") => {
  if (view === "world") return geoNaturalEarth1().fitExtent([[80, 90], [W - 80, H - 40]], {type: "FeatureCollection", features: feats} as any);
  return geoNaturalEarth1().center([12, 53]).scale(2300).translate([W / 2, H / 2]);
};

type Pin = {id?: string; lonlat?: [number, number]; at: number; label?: string; color?: string};

/** Weltkarte: Laender dunkel, Hervorhebungen, Punkte-Schwaerme, Verbindungslinien, Pins */
export const WorldMap: React.FC<{
  view?: "world" | "europe"; highlight?: {id: string; at: number; color?: string}[];
  swarm?: {at: number; dur: number; n: number; color?: string}; links?: {at: number; n: number};
  pins?: Pin[]; pulseAll?: number; zoom?: [number, number, number, number]; // [t0,t1,from,to]
  dim?: number;
}> = ({view = "world", highlight = [], swarm, links, pins = [], pulseAll, zoom, dim = 1}) => {
  const f = useCurrentFrame();
  const proj: GeoProjection = useMemo(() => makeProj(view), [view]);
  const path = useMemo(() => geoPath(proj), [proj]);
  const paths = useMemo(() => feats.map((d) => ({id: d.id, d: path(d) || ""})), [path]);
  // Schwarm-Punkte: zufaellige Punkte in Landflaechen (ueber Laender-Zentroide gestreut)
  const pts = useMemo(() => {
    if (!swarm) return [];
    const big = feats.map((d) => ({c: proj(geoCentroid(d)) as [number, number], area: path.area(d)})).filter((x) => x.c && x.area > 40);
    const tot = big.reduce((a, b) => a + Math.sqrt(b.area), 0);
    const out: {x: number; y: number; t: number}[] = [];
    let k = 0;
    while (out.length < swarm.n && k < swarm.n * 5) {
      const r = random(`p${k}`) * tot; let acc = 0; let pick = big[0];
      for (const b of big) { acc += Math.sqrt(b.area); if (acc >= r) { pick = b; break; } }
      const rad = Math.sqrt(pick.area) * 0.35;
      out.push({x: pick.c[0] + (random(`x${k}`) - 0.5) * rad, y: pick.c[1] + (random(`y${k}`) - 0.5) * rad, t: random(`t${k}`)});
      k++;
    }
    return out;
  }, [swarm, proj, path]);
  const z = zoom ? interpolate(f, [s(zoom[0]), s(zoom[1])], [zoom[2], zoom[3]], {...clamp, easing: ease}) : 1;
  return (
    <AbsoluteFill style={{transform: `scale(${z})`, opacity: dim}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          <filter id="glow"><feGaussianBlur stdDeviation="4" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        </defs>
        {paths.map((p) => {
          const h = highlight.find((x) => x.id === p.id);
          const ho = h ? interpolate(f, [s(h.at), s(h.at) + 8], [0, 1], clamp) : 0;
          const col = h?.color || AMBER;
          return <path key={p.id} d={p.d} fill={ho > 0 ? col : "#1A2030"} fillOpacity={ho > 0 ? 0.25 + ho * 0.55 : 1}
            stroke={ho > 0 ? col : "#2B3448"} strokeWidth={ho > 0 ? 1.6 : 0.8} filter={ho > 0.5 ? "url(#glow)" : undefined} />;
        })}
        {swarm && pts.map((p, i) => {
          const at = s(swarm.at) + p.t * s(swarm.dur);
          const o = interpolate(f, [at, at + 6], [0, 1], clamp);
          const ring = interpolate(f, [at, at + 14], [0, 1], clamp);
          return <g key={i} opacity={o}>
            <circle cx={p.x} cy={p.y} r={2.6} fill={swarm.color || AMBER} filter="url(#glow)" />
            {ring < 1 && <circle cx={p.x} cy={p.y} r={2 + ring * 14} fill="none" stroke={swarm.color || AMBER} strokeOpacity={1 - ring} strokeWidth={1.5} />}
          </g>;
        })}
        {links && pts.slice(0, links.n * 2).map((p, i) => {
          if (i % 2) return null; const q = pts[(i * 7 + 13) % pts.length];
          const at = s(links.at) + (i / (links.n * 2)) * s(1.4);
          const pr = interpolate(f, [at, at + 12], [0, 1], {...clamp, easing: ease});
          const mx = (p.x + q.x) / 2, my = Math.min(p.y, q.y) - Math.abs(p.x - q.x) * 0.25;
          const len = Math.hypot(q.x - p.x, q.y - p.y) * 1.3;
          return <path key={`l${i}`} d={`M${p.x},${p.y} Q${mx},${my} ${q.x},${q.y}`} fill="none" stroke={AMBER} strokeOpacity={0.55} strokeWidth={1.4}
            strokeDasharray={`${len}`} strokeDashoffset={len * (1 - pr)} />;
        })}
        {pins.map((pn, i) => {
          const ll = pn.lonlat || (geoCentroid(byId(pn.id!)) as [number, number]);
          const [x, y] = proj(ll) as [number, number];
          const sp = interpolate(f, [s(pn.at), s(pn.at) + 8], [0, 1], {...clamp, easing: ease});
          if (sp <= 0) return null;
          const pulse = pulseAll !== undefined && f >= s(pulseAll) ? ((f - s(pulseAll)) % 18) / 18 : ((f - s(pn.at)) % 24) / 24;
          const col = pn.color || RED;
          return <g key={`pin${i}`} transform={`translate(${x},${y}) scale(${sp})`}>
            <circle r={10 + pulse * 40} fill="none" stroke={col} strokeOpacity={(1 - pulse) * 0.9} strokeWidth={3} />
            <circle r={9} fill={col} filter="url(#glow)" />
            <circle r={3.5} fill="#fff" />
            {pn.label && <g transform="translate(16,-14)">
              <rect x={0} y={-22} width={pn.label.length * 14 + 24} height={34} rx={4} fill="rgba(10,12,18,0.85)" stroke={col} strokeWidth={1.5} />
              <text x={12} y={2} fill={INK} fontFamily={FONT} fontWeight={700} fontSize={20} letterSpacing={1.5}>{pn.label}</text>
            </g>}
          </g>;
        })}
      </svg>
    </AbsoluteFill>
  );
};

export const allIds = feats.map((d) => d.id as string);
export const muted = MUTED;
