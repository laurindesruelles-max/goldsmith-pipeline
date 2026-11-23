import {bundle} from "@remotion/bundler";
import {renderStill, selectComposition} from "@remotion/renderer";
import path from "path";
const times = process.argv.slice(2).map(Number);
const serveUrl = await bundle({entryPoint: path.resolve("src/index.ts")});
const comp = await selectComposition({serveUrl, id: "Main", browserExecutable: "/usr/bin/google-chrome"});
for (const t of times) {
  await renderStill({serveUrl, composition: comp, frame: Math.round(t * 30), output: `/tmp/st/${t}.png`, browserExecutable: "/usr/bin/google-chrome", scale: 0.5});
  console.log("ok", t);
}
