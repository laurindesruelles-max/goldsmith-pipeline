import json, subprocess, case as C
import os
m2 = json.load(open('build/meta2.json'))
FIRST = m2['plan'][0][0]
m1 = {"plan": C.PLAN, "sfx": C.sfx_events()} if FIRST > 1 else {"plan": [], "sfx": []}
plan = m1['plan'] + [tuple(x) for x in m2['plan']]; sfx = m1['sfx'] + m2['sfx']; total = m2['end']
parts = []
for n, T in plan:
    o = f'build/a{n}.wav'
    src = f'build/vo/{n}.wav' if os.path.exists(f'build/vo/{n}.wav') else f'../audio/{n}.wav'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',src,'-af',f'aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{T:.4f}',o],check=True); parts.append(o)
open('build/al.txt','w').write(''.join(f"file '{p.split('/')[-1]}'\n" for p in parts))
open('build/vl.txt','w').write(''.join(f"file 's{n}.mp4'\n" for n,_ in plan))
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','build/al.txt','-c','copy','build/voice_full.wav'],check=True)
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','build/vl.txt','-c','copy','build/video_full.mp4'],check=True)
seen=set(); ev=[]
for t,nm,g in sorted(tuple(x) for x in sfx):
    k=(round(t,2),nm)
    if k in seen or t<0: continue
    seen.add(k); ev.append((t,nm,g))
# premix sfx in chunks (too many inputs for one amix)
chunks=[ev[i:i+150] for i in range(0,len(ev),150)]; fx=[]
for ci,ch in enumerate(chunks):
    inputs=[]; fc=[]
    for i,(t,nm,g) in enumerate(ch):
        if nm.startswith('key'): nm=f'key{(i*5)%8}'; g*=0.75
        ms=int(t*1000)
        if nm.startswith('clip:'):   # Objekt-Geräusche eines 3D-Clips: "clip:<pfad>:<tempo>"
            cp = nm[5:nm.rfind(':')]; rate = float(nm[nm.rfind(':')+1:])
            inputs+=['-i',cp]; tempo = f',atempo={max(0.5,rate):.3f}' if rate < 0.999 else ''
            fc.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo{tempo},volume={g},adelay={ms}|{ms},apad=whole_dur={total:.3f}[s{i}]')
            continue
        if nm.startswith('amb:'):   # Raumklang: "amb:<datei>:<dauer>" -> geloopt, ein-/ausgeblendet
            _, an, ad = nm.split(':'); ad=float(ad); fo=min(0.8, ad/3)
            inputs+=['-stream_loop','-1','-i',f'sfx/{an}.wav']
            fc.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{ad:.3f},afade=t=in:d={fo:.2f},afade=t=out:st={ad-fo:.3f}:d={fo:.2f},volume={g},adelay={ms}|{ms},apad=whole_dur={total:.3f}[s{i}]')
            continue
        inputs+=['-i',f'sfx/{nm}.wav']
        fc.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g},adelay={ms}|{ms},apad=whole_dur={total:.3f}[s{i}]')
    fc.append(''.join(f'[s{i}]' for i in range(len(ch)))+f'amix=inputs={len(ch)}:normalize=0:duration=longest,atrim=0:{total:.3f}[o]')
    o=f'build/fx{ci}.wav'; fx.append(o)
    subprocess.run(['ffmpeg','-y','-loglevel','error',*inputs,'-filter_complex',';'.join(fc),'-map','[o]',o],check=True)
# ---- Musikbett: Track je Kapitel (spec "music"), Crossfades, Abtauchen bei Spannungspausen ----
import numpy as np, scipy.io.wavfile as wf
def load_track(name):
    p = f'build/{name}.wav'
    if not os.path.exists(p):
        src = name if name.endswith('.mp3') else (f'music/{name}.mp3' if os.path.exists(f'music/{name}.mp3') else f'{name}.mp3')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',src,'-ar','48000','-ac','2',p],check=True)
    return wf.read(p)[1].astype(np.float32)/32768
SR=48000; N=int(total*SR)+SR; bed=np.zeros((N,2),np.float32)
# audiokit (18.11.2026): Musik lebt mehr – lange Kapitel springen alle ~65 s auf eine andere (spannendere) Stelle desselben Tracks
# (Charakter bleibt gleich), und vor jeder bewussten Musikpause schwillt die Musik 3 s an (Crescendo in die Stille).
# Sounds bleiben unangetastet (Laurins Goldsmith-Sounds). Ausschalten: GOLDSMITH_AK=0
AK_ON = os.environ.get("GOLDSMITH_AK", "1") != "0"
def vary(tr, L, part=65.0, xf=2.0):
    w = SR; n = len(tr) // w; e = np.sqrt((tr[:n*w].reshape(n, w, 2)**2).mean(axis=(1, 2))); P = int(part); X = int(xf*SR)
    win = np.convolve(e, np.ones(P)/P, 'valid') if n > P else np.array([e.mean()])
    order = list(np.argsort(win)[::-1]); out = np.zeros((0, 2), np.float32); used = [0]; k = 0
    while len(out) < L:
        off = 0 if k == 0 else next((o for o in order if all(abs(o-u) > P*0.5 for u in used)), order[k % len(order)])
        used.append(off); piece = np.concatenate([tr[int(off)*w:]] + [tr]*2)[:int(part*SR)+X].copy()
        if len(out): r = min(X, len(out)); piece[:r] *= np.linspace(0, 1, r)[:, None]; out[-r:] *= np.linspace(1, 0, r)[:, None]; out = np.concatenate([out[:-r], out[-r:] + piece[:r], piece[r:]])
        else: out = piece
        k += 1
    return out[:L]
cues=[tuple(c) for c in m2.get('music',[[0,'crime_archive']])]; XF=int(2.5*SR)
# Laurin 16.11.: vor jedem Musikwechsel (= Kapitel) Musik ausblenden, kurze Stille, neuer Track setzt mit der Kapitelkarte ein
FO=int(2.2*SR); GAP=int(0.5*SR); FI=int(1.2*SR)
# Laurin 17.11. (dritte Fassung): an Kapitelkarten bricht die alte Musik genau mit dem Bass-Hit ab (Karte +0,6 s, nur 40 ms Blende),
# die Karte steht ohne Musik, der neue Track beginnt 4 s nach Kapitelbeginn leise und wird über 2,5 s normal laut.
# Wechsel mitten im Kapitel wie bisher (Ausblenden, 0,5 s Stille).
CARD_CUT=0.6; CARD_IN=4.0; CARD_FI=int(2.5*SR); CUT_FO=int(0.04*SR)
for i,c in enumerate(cues):
    t0,name=c[0],c[1]; at_card = c[2] if len(c)>2 else True
    nxt_card = (cues[i+1][2] if len(cues[i+1])>2 else True) if i+1<len(cues) else False
    t1 = cues[i+1][0] if i+1<len(cues) else total
    a=int(t0*SR)+(int((CARD_IN if at_card else 0.55)*SR) if i>0 else 0)
    if i+1<len(cues): b=min(N,int((t1+CARD_CUT)*SR) if nxt_card else int(t1*SR)-GAP)
    else: b=N
    tr=load_track(name)
    if b<=a: continue
    seg=np.concatenate([tr]*(1+(b-a)//len(tr)))[:b-a].copy()
    if AK_ON and len(seg) > 75*SR: seg = vary(tr, len(seg))   # audiokit: kein Track > ~65 s am Stück gleich
    if i>0 and at_card: ramp=min(CARD_FI,len(seg)); seg[:ramp]*=np.linspace(0.25,1,ramp)[:,None]; seg[:int(0.15*SR)]*=np.linspace(0,1,min(len(seg),int(0.15*SR)))[:,None]
    else: ramp=min(FI,len(seg)); seg[:ramp]*=np.linspace(0,1,ramp)[:,None]
    if i+1<len(cues): k=min(CUT_FO if nxt_card else FO,len(seg)); seg[-k:]*=np.linspace(1,0,k)[:,None]
    bed[a:a+len(seg)]+=seg
env=np.ones(N,np.float32)
for d0,d1 in m2.get('dips',[]):
    a=int(d0*SR); b=int(d1*SR); r=int(0.25*SR)
    env[a:b]=0.12; env[max(0,a-r):a]=np.minimum(env[max(0,a-r):a],np.linspace(1,0.12,a-max(0,a-r)))
    env[b:b+r]=np.minimum(env[b:b+r],np.linspace(0.12,1,len(env[b:b+r])))
for d0,d1 in m2.get('rests',[]):   # bewusste Musikpausen (Spannung)
    a=int(d0*SR); b=min(N,int(d1*SR)); r=int(0.8*SR)
    if AK_ON:   # Crescendo in die Stille: 3 s vor der Pause bis +3,5 dB
        s0=max(0,a-r-int(3*SR)); env[s0:a-r]*=10**(3.5*np.linspace(0,1,a-r-s0)**1.5/20)
    env[a:b]=0.0
    env[max(0,a-r):a]=np.minimum(env[max(0,a-r):a],np.linspace(1,0,a-max(0,a-r)))
    env[b:b+r]=np.minimum(env[b:b+r],np.linspace(0,1,len(env[b:b+r])))
for dk in m2.get('ducks',[]):   # 3D-Szenen ~60 %, Daten-Grafiken ~28 % (Musik fast weg, Daten-Sounds stehen frei)
    d0,d1=dk[0],dk[1]; lv=dk[2] if len(dk)>2 else 0.6
    a=int(d0*SR); b=min(N,int(d1*SR)); r=int(0.6*SR)
    env[a:b]=np.minimum(env[a:b],lv)
    env[max(0,a-r):a]=np.minimum(env[max(0,a-r):a],np.linspace(1,lv,a-max(0,a-r)))
    env[b:b+r]=np.minimum(env[b:b+r],np.linspace(lv,1,len(env[b:b+r])))
bed*=env[:,None]
wf.write('build/music_bed.wav',SR,(np.clip(bed[:int(total*SR)],-1,1)*32767).astype(np.int16))
inp=['-i','build/voice_full.wav','-i','build/music_bed.wav']
for o in fx: inp+=['-i',o]
k=len(fx)
fc=[''.join(f'[{i+2}:a]' for i in range(k))+f'amix=inputs={k}:normalize=0,volume=0.8[fx]',
    f'[0:a]apad=pad_dur=3,loudnorm=I=-16:TP=-1.5,atrim=0:{total:.3f},asplit=2[v][sc]',
    f'[1:a]atrim=0:{total:.3f},volume=0.42,afade=t=out:st={total-3:.2f}:d=3[m]',
    '[m][sc]sidechaincompress=threshold=0.04:ratio=3.5:attack=30:release=500[md]',
    f'[v][md][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95,atrim=0:{total:.3f}[out]']
subprocess.run(['ffmpeg','-y','-loglevel','error',*inp,'-filter_complex',';'.join(fc),'-map','[out]','-c:a','aac','-b:a','192k','build/mix_full.m4a'],check=True)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','build/video_full.mp4','-i','build/mix_full.m4a','-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','22','-maxrate','14M','-bufsize','28M','-pix_fmt','yuv420p','-c:a','copy','-shortest','-movflags','+faststart','build/full.tmp.mp4'],check=True)
import os; os.replace('build/full.tmp.mp4',os.environ.get('OUT','../FINAL.mp4'))
_ak = os.environ.get("AUDIOKIT", "/home/claude/audiokit")
if os.path.exists(f"{_ak}/adapter.py"):   # Endkontrolle (nur Bericht, ändert nichts)
    import sys; sys.path.insert(0, _ak); import adapter as AK
    AK.final_check(os.environ.get('OUT','../FINAL.mp4'), 'build/voice_full.wav', 'build/music_bed.wav'); AK.write_report('build/ton_bericht.txt')
print(len(ev),'sfx',total)
