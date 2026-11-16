"""Mischt die Objekt-Geräusche eines Diorama-Clips (meta.json "cues") zu <clip>/cues.wav.
Jedes Geräusch folgt seinem Objekt: Lautstärke nach Entfernung zur Kamera, Stereo nach Bildposition.
Fehlende Sounddateien werden übersprungen (Warnung).
usage: python3 cues.py <clip_dir> <sfx_dir>
"""
import os, sys, json, subprocess, numpy as np

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def build(clip, sfx, force=False):
    out = f"{clip}/cues.wav"
    meta = json.load(open(f"{clip}/meta.json"))
    if os.path.exists(out) and not force and os.path.getmtime(out) > os.path.getmtime(f"{clip}/meta.json"): return out
    n = len([f for f in os.listdir(clip) if f.startswith("f_")]); total = n/meta.get("fps", 24) + 1.0
    mix = np.zeros((int(total*SR), 2), np.float32)
    for c in meta.get("cues", []):
        p = f"{sfx}/{c['name']}.wav"
        if not os.path.exists(p): print("WARNUNG: Sound fehlt:", c["name"]); continue
        s = load(p); tr = np.array(c["track"], np.float32)
        if c["loop"]: t0 = float(tr[0, 0]); dur = max(float(c["dur"]), 0.0)
        else:
            dur = len(s)/SR; an = float(c.get("anchor", tr[0, 0])); al = c.get("align", "start")
            t0 = an - (dur if al == "end" else dur/2 if al == "center" else 0)
            if t0 < 0: s = s[int(-t0*SR):]; dur = len(s)/SR; t0 = 0.0
        L = int(dur*SR) if c["loop"] else len(s)
        if L <= 0: continue
        if c["loop"]:
            s = np.concatenate([s]*(1+L//len(s)))[:L]
            fo = min(int(0.4*SR), L//4); s[:fo] *= np.linspace(0, 1, fo)[:, None]; s[-fo:] *= np.linspace(1, 0, fo)[:, None]
        tt = t0 + np.arange(L)/SR
        g = np.interp(tt, tr[:, 0], tr[:, 1]); pan = np.interp(tt, tr[:, 0], tr[:, 2])
        lg = np.sqrt(np.clip(0.5-pan/2, 0, 1)); rg = np.sqrt(np.clip(0.5+pan/2, 0, 1))
        mono = s.mean(1)
        a = int(t0*SR); b = min(len(mix), a+L)
        mix[a:b, 0] += (mono*g*lg*1.41)[:b-a]; mix[a:b, 1] += (mono*g*rg*1.41)[:b-a]
    pk = np.abs(mix).max()
    if pk > 0.98: mix *= 0.98/pk
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", out], input=mix.tobytes(), check=True)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2], force=True))
