"""Ton-Mix der ANOM-Stilprobe: Stimme, Effekte auf Bild-Ereignissen, Musik mit Ducking/Swells/Pausen, Master -14 LUFS / TP -2 dB.
usage: python3 mix.py <video_in> <video_out>"""
import sys, subprocess, json, wave, numpy as np
SR = 48000; DUR = 62.0
X = "/home/claude/anom/sfx/"; V = "/home/claude/anom/vo/"
MUSIC = "/home/claude/goldsmith-pipeline/assets/music/suspense_pulse.mp3"

def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
C = {}
def clip(p):
    if p not in C: C[p] = load(p)
    return C[p]
def place(buf, a, t, g):
    i = int(t * SR)
    if i >= len(buf) or i < 0: return
    a = a[:len(buf) - i]; buf[i:i + len(a)] += a * g

LINES = {1: 0.4, 2: 9.9, 3: 18.5, 4: 25.0, 5: 29.8, 6: 35.3, 7: 42.4, 8: 46.7, 9: 53.3}
voice = np.zeros((int(DUR * SR), 2), np.float32)
for k, t in LINES.items():
    a = clip(f"{V}{k}.mp3"); a = a / (np.sqrt((a ** 2).mean()) + 1e-9) * 0.1   # gleich laut
    place(voice, a, t, 1.0)

def keys(t0, n, step=0.075, g=0.22):
    return [(t0 + i * step, f"{X}key{i % 8}.wav", g * (0.8 + 0.4 * ((i * 37) % 10) / 10)) for i in range(n)]
def ticks(t0, dur, n=12, g=0.16):   # Zaehler: Tick-Folge, bremst aus und wird leiser
    out = []
    for i in range(n):
        u = i / (n - 1); tt = t0 + dur * (1 - (1 - u) ** 2.2)
        out.append((tt, X + "tick.wav", g * (1 - 0.6 * u)))
    return out

E = []
# A Hook (3D)
E += keys(0.38, 9)
E += [(1.12, X + "phone_notify.wav", 0.32)]
E += ticks(3.1, 0.9) + [(3.95, X + "price_tag.wav", 0.35)]
# B Karte
E += [(4.92, X + "diagram_whoosh.wav", 0.35)] + [(5.05 + i * 0.19, X + "pin_pop.wav", 0.12 + 0.02 * (i % 3)) for i in range(7)]
E += [(5.4, X + "text_click.wav", 0.35)]
# C Chat
E += [(7.18, X + "whoosh.wav", 0.18)] + [(t, X + "pin_pop.wav", 0.16) for t in (7.3, 7.65, 8.05, 8.35)]
E += keys(8.3, 10, 0.05, 0.14)
# D App-Reveal
E += [(9.85, X + "diagram_whoosh.wav", 0.4), (9.95, X + "sub_drop.wav", 0.35), (10.65, X + "data_loading.wav", 0.16), (11.1, X + "text_click.wav", 0.3)]
# E Ein-App-Handy
E += [(11.88, X + "whoosh.wav", 0.22), (12.4, X + "marker_stroke.wav", 0.28), (12.7, X + "marker_stroke2.wav", 0.26), (13.0, X + "marker_stroke.wav", 0.24),
      (13.5, X + "pin_pop.wav", 0.3), (13.62, X + "text_click.wav", 0.35)]
# F Verschluesselung
E += [(14.45, X + "diagram_whoosh.wav", 0.3), (14.8, X + "glitch.wav", 0.24), (14.85, X + "data_loading.wav", 0.18), (15.4, X + "text_click.wav", 0.3)]
# G Fernloeschung
E += [(16.28, X + "whoosh.wav", 0.2), (17.02, X + "mouse_click.wav", 0.45), (17.25, X + "paper_slide.wav", 0.2), (17.4, X + "whoosh.wav", 0.18), (17.85, X + "price_tag.wav", 0.22)]
# H Organisationen
E += [(18.42, X + "diagram_whoosh.wav", 0.45)] + [(18.6 + i * 0.13, X + "pin_pop.wav", 0.08) for i in range(9)]
E += ticks(19.4, 1.0) + [(20.1, X + "text_click.wav", 0.32)]
# I 100 Laender
E += [(22.55, X + "diagram_whoosh.wav", 0.32)] + ticks(22.7, 1.0)
# K Pause -> Enthuellung
E += [(24.3, X + "heartbeat.wav", 0.32), (24.55, X + "keys" if False else X + "key3.wav", 0.0)] + keys(24.55, 16, 0.05, 0.12)
E += [(26.28, X + "glitch.wav", 0.45), (26.45, X + "glitch.wav", 0.3), (27.3, X + "riser.wav", 0.28),
      (28.3, X + "whoosh.wav", 0.4), (28.45, X + "sub_drop.wav", 2.6), (28.47, X + "zoom_deep_impact.wav", 2.0), (27.3, X + "riser.wav", 0.35)]
# L Kopie
E += [(29.75, X + "diagram_whoosh.wav", 0.3), (30.2, X + "whoosh.wav", 0.18), (31.4, X + "glitch.wav", 0.3), (31.5, X + "pin_pop.wav", 0.3)] + keys(31.8, 14, 0.04, 0.12)
# M Serverraum (3D): Brummen + Zaehler
E += [(32.95, X + "zoom_riser.wav", 0.0), (33.0, X + "neon_buzz.wav", 0.16), (36.0, X + "neon_buzz.wav", 0.0), (33.0, X + "data_loading.wav", 0.12)]
E += ticks(35.4, 1.5, 14) + [(36.9, X + "whoosh.wav", 0.22)]
# N 27 Mio.
E += ticks(37.0, 1.6, 16) + [(37.9, X + "text_click.wav", 0.33)]
# O Deutsch + Pause
E += [(39.42, X + "diagram_whoosh.wav", 0.45), (40.8, X + "pin_pop.wav", 0.35), (40.85, X + "text_click.wav", 0.3)]
E += keys(42.0, 9, 0.083, 0.26)
# P Zugriff
E += [(42.4, X + "sub_drop.wav", 0.7), (42.42, X + "hammer.wav", 0.25)] + [(43.95 + i * 0.06, X + "pin_pop.wav", 0.1 + 0.02 * (i % 4)) for i in range(16)]
E += [(45.0, X + "heartbeat.wav", 0.4)]
# Q Beweismittel (3D): Kamerablitze, Zahlen
E += [(46.6, X + "whoosh.wav", 0.25), (48.62, X + "shutter.wav", 0.32), (51.17, X + "shutter.wav", 0.26)]
E += ticks(46.85, 0.7, 10) + [(47.0, X + "text_click.wav", 0.32)] + ticks(48.85, 0.7, 6) + [(49.0, X + "text_click.wav", 0.32)] + ticks(50.55, 0.7, 10) + [(50.7, X + "text_click.wav", 0.32)]
# R Gerichte
E += [(52.82, X + "diagram_whoosh.wav", 0.45)] + [(53.0 + i * 0.16, X + "paper_slide.wav", 0.16) for i in range(5)]
E += [(54.6, X + "hammer.wav", 0.55), (54.62, X + "sub_drop.wav", 0.4)] + keys(53.5, 18, 0.036, 0.1)
# S Schluss: Bildschirm erlischt
E += [(56.33, X + "diagram_whoosh.wav", 0.4), (56.55, X + "text_click.wav", 0.28), (58.2, X + "glitch.wav", 0.4), (58.24, X + "sub_drop.wav", 0.8), (59.8, X + "sub_drop.wav", 1.2), (59.8, X + "zoom_deep_impact.wav", 0.45), (59.82, X + "text_click.wav", 0.3)]

def build(music_gain=0.32):
    sfx = np.zeros_like(voice)
    for j, (t, p, g) in enumerate(E):
        if g <= 0: continue
        pan = ((j * 37) % 11 - 5) / 5 * 0.45
        a = clip(p) * np.array([1 - max(0, pan), 1 + min(0, pan)], np.float32)
        place(sfx, a, t, g)
    # Musik: Bett mit Ducking unter der Stimme, Pausen vor grossen Saetzen, Swells
    m = clip(MUSIC); n = len(voice)
    while len(m) < n: m = np.concatenate([m, clip(MUSIC)])
    m = m[:n].copy(); tt = np.arange(n) / SR
    env = np.ones(n, np.float32) * music_gain
    # Ducking: Huellkurve der Stimme (gegaettet, 120 ms Attack/400 ms Release)
    vr = np.abs(voice).mean(1); hop = SR // 100
    fr = np.array([vr[i:i + hop].max() for i in range(0, n, hop)])
    act = (fr > 0.01).astype(float); sm = np.zeros_like(act); a = 0
    for i, x in enumerate(act):
        a = a + (x - a) * (0.35 if x > a else 0.05); sm[i] = a
    depth = np.full(n, 9.0, np.float32); w = (tt > 28.3) & (tt < 31.6); depth[w] = 3.0
    duck = 10 ** (-depth * np.repeat(sm, hop)[:n] / 20); env *= duck
    for t0, t1, fade in [(24.05, 24.9, 0.25), (41.45, 42.38, 0.2), (58.15, 58.6, 0.08)]:   # Musik kurz weg
        g = np.ones(n); g[(tt > t0) & (tt < t1)] = 0
        ram = (tt >= t0 - fade) & (tt <= t0); g[ram] = 1 - (tt[ram] - (t0 - fade)) / fade
        ram = (tt >= t1) & (tt <= t1 + 0.4); g[ram] = (tt[ram] - t1) / 0.4
        env *= g
    for ts, db, d in [(23.6, 5, 1.4), (29.0, 13, 3.2), (41.0, 5, 1.2), (45.5, 4, 1.6), (57.8, 4, 1.2), (60.0, 6, 1.5)]:
        sh = np.clip(1 - np.abs(tt - ts) / d, 0, 1); env *= 10 ** (db * sh / 20)
    fi = int(0.8 * SR); env[:fi] *= np.linspace(0, 1, fi)
    fo = int(0.7 * SR); env[-fo:] *= np.linspace(1, 0, fo)
    mm = m * env[:, None]; d = int(0.014 * SR)
    mm[d:, 1] = 0.55 * mm[d:, 1] + 0.45 * mm[:-d, 1]; mm[d:, 0] = 0.55 * mm[d:, 0] + 0.45 * mm[:-d, 0][::1] * 0 + 0.45 * mm[d:, 0]
    return voice + sfx + mm

def lufs(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(o[o.rindex("{"):o.rindex("}") + 1]); return float(j["input_i"]), float(j["input_tp"])

if __name__ == "__main__":
    vin, vout = sys.argv[1], sys.argv[2]
    buf = build(); buf = buf / (np.abs(buf).max() + 1e-9) * 0.5
    tmp = "/tmp/anom_mix.wav"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf, -1, 1) * 32767).astype("<i2").tobytes())
    i, _ = lufs(tmp); gain = -14.0 - i + 1.0
    for _ in range(3):
        af = (f"highpass=f=35,deesser=i=0.25,equalizer=f=70:width_type=o:width=1:g=1.5,equalizer=f=2000:width_type=o:width=1.2:g=3,"
              f"volume={gain:.2f}dB,alimiter=limit={10 ** (-2.3 / 20):.3f}:level=false")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vin, "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", af,
                        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", str(DUR), vout], check=True)
        got, tp = lufs(vout)
        if abs(got - (-14.0)) < 0.5: break
        gain += (-14.0 - got)
    print("LUFS", lufs(vout))
