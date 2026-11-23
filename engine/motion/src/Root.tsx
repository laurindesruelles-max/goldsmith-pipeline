import React from "react";
import {Composition, AbsoluteFill} from "remotion";
import {FPS, Grain, Drift} from "./lib";
import * as C from "./comps";

const MAP: Record<string, React.FC<any>> = {map: C.MapC, flow: C.FlowC, flip: C.FlipC, counter: C.CounterC, grid: C.GridC, phone: C.PhoneC, cipher: C.CipherC, stack: C.StackC};
type P = {comp: string; props: any; len: number};
const Motion: React.FC<P> = ({comp, props, len}) => {
  const Comp = MAP[comp];
  return <AbsoluteFill style={{background: "#000"}}><Drift len={len}><Comp {...props} len={len} /></Drift><Grain /></AbsoluteFill>;
};
export const Root: React.FC = () => (
  <Composition id="Motion" component={Motion as any} fps={FPS} width={1920} height={1080} durationInFrames={180}
    defaultProps={{comp: "counter", props: {value: 27000000, caption: "MESSAGES"}, len: 6}}
    calculateMetadata={({props}: any) => ({durationInFrames: Math.round((props.len || 6) * FPS)})} />
);
