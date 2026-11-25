"""timing.json aus audio/N.wav (ffmpeg silencedetect noise=-35dB d=0.12) – Format wie 001/004."""
import json, re, subprocess, sys
A = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/work/audio"; N = int(sys.argv[2]) if len(sys.argv) > 2 else 71
out = {}
for n in range(1, N+1):
    f = f"{A}/{n}.wav"
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
    log = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    segs, cur = [], 0.0
    for i, s in enumerate(st):
        if s > cur + 0.05: segs.append([round(cur, 4), round(s, 4)])
        cur = en[i] if i < len(en) else dur
    if cur < dur - 0.05: segs.append([round(cur, 4), round(dur, 4)])
    out[str(n)] = {"dur": round(dur, 4), "segs": segs}
json.dump(out, open("timing.json", "w"))
print("ok", sum(v["dur"] for v in out.values()))
