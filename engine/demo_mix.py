import json, sys, os, subprocess, numpy as np, scipy.io.wavfile as wf
SR = 48000
scenes = [int(x) for x in sys.argv[2:]]; out = sys.argv[1]
m = json.load(open("build/meta2.json")); plan = dict((n, T) for n, T in m["plan"])
S0 = {}; acc = 0.0
for n, T in m["plan"]: S0[n] = acc; acc += T
def load(p):
    tmp = "/tmp/_l.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, "-ar", str(SR), "-ac", "2", tmp], check=True)
    return wf.read(tmp)[1].astype(np.float32)/32768
total = sum(plan[n] for n in scenes); N = int(total*SR)+SR
voice = np.zeros((N, 2), np.float32); sfx = np.zeros((N, 2), np.float32); env = np.ones(N, np.float32)
pos = 0.0; cache = {}
for n in scenes:
    T = plan[n]; v = f"build/vo/{n}.wav" if os.path.exists(f"build/vo/{n}.wav") else f"../audio/{n}.wav"
    a = load(v)[:int(T*SR)]; i = int(pos*SR); voice[i:i+len(a)] += a
    for t, name, g in m["sfx"]:
        if S0[n] <= t < S0[n]+T and not str(name).startswith(("amb:", "clip:")):
            p = f"sfx/{name}.wav"
            if not os.path.exists(p): continue
            if name not in cache: cache[name] = load(p)
            s = cache[name]*float(g); j = int((pos+t-S0[n])*SR); s = s[:max(0, N-j)]; sfx[j:j+len(s)] += s
    for dk in m.get("ducks", []):
        d0, d1 = dk[0], dk[1]; lv = dk[2] if len(dk) > 2 else 0.6
        if S0[n] <= d0 < S0[n]+T:
            a0 = int((pos+d0-S0[n])*SR); a1 = min(N, int((pos+min(d1, S0[n]+T)-S0[n])*SR)); env[a0:a1] = np.minimum(env[a0:a1], lv)
    pos += T
env = np.convolve(env, np.ones(int(0.4*SR))/int(0.4*SR), mode="same")
mus = load("music/suspense_pulse.mp3"); mus = np.concatenate([mus]*(1+N//len(mus)))[:N]*0.16*env[:, None]
mix = voice*1.0 + sfx*0.9 + mus
mix = mix/max(1.0, np.abs(mix).max()/0.95)
wf.write("/tmp/demo_a.wav", SR, (mix*32767).astype(np.int16))
open("/tmp/demo_v.txt", "w").write("".join(f"file '{os.path.abspath(f'build/s{n}.mp4')}'\n" for n in scenes))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "/tmp/demo_v.txt", "-i", "/tmp/demo_a.wav", "-map", "0:v", "-map", "1:a",
                "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
print("ok", out, round(total, 1))
