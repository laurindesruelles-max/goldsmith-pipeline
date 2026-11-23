import React from "react";
import {AbsoluteFill, Sequence, OffthreadVideo, staticFile, useCurrentFrame, interpolate} from "remotion";
import {s, Shot, Grain, clamp} from "./lib";
import * as S from "./scenes";

const Clip: React.FC<{src: string; rate?: number}> = ({src, rate = 1}) => (
  <AbsoluteFill>
    <OffthreadVideo src={staticFile(src)} playbackRate={rate} muted style={{width: "100%", height: "100%", objectFit: "cover"}} />
    <AbsoluteFill style={{background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.55) 100%)"}} />
  </AbsoluteFill>
);
const Flash: React.FC<{at: number; color?: string}> = ({at, color = "#fff"}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [s(at), s(at) + 2, s(at) + 8], [0, 0.55, 0], clamp);
  return <AbsoluteFill style={{background: color, opacity: o, pointerEvents: "none"}} />;
};
type Item = [number, number, React.FC, boolean?];
const T: Item[] = [
  [0.0, 5.0, () => <><Clip src="hook.mp4" /><S.HookOverlay /></>, true],
  [5.0, 7.2, S.SwarmMap], [7.2, 9.9, S.ChatScene], [9.9, 11.9, S.AppReveal], [11.9, 14.5, S.OneApp],
  [14.5, 16.3, S.Cipher], [16.3, 18.5, S.Wipe], [18.5, 22.6, S.Orgs], [22.6, 24.3, S.Countries],
  [24.3, 29.8, S.Reveal], [29.8, 33.0, S.CopyFlow],
  [33.0, 37.0, () => <><Clip src="server.mp4" /><S.ServerOverlay at={2.4} /></>, true],
  [37.0, 39.5, S.Messages], [39.5, 42.4, S.German], [42.4, 46.6, S.Raids],
  [46.6, 52.9, () => <><Clip src="evidence.mp4" /><S.EvidenceOverlay /></>, true],
  [52.9, 56.4, S.Courts],
  [56.4, 62.0, () => <><Clip src="end.mp4" /><S.EndOverlay /></>, true],
];
export const TOTAL = 62.0;
export const Main: React.FC = () => (
  <AbsoluteFill style={{background: "#000"}}>
    {T.map(([a, b, C, is3d], i) => (
      <Sequence key={i} from={s(a)} durationInFrames={s(b) - s(a)}>
        <Shot dur={b - a} drift={is3d ? 0.0 : 0.035} inZoom={i === 0 ? 1.0 : 1.08}><C /></Shot>
      </Sequence>
    ))}
    {[5.0, 9.9, 24.3, 33.0, 42.4, 46.6, 56.4].map((t) => <Flash key={t} at={t} />)}
    <Flash at={28.45} color="#ff2a2a" />
    <Grain />
  </AbsoluteFill>
);
