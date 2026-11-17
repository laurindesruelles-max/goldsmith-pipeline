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
cues=[tuple(c) for c in m2.get('music',[[0,'crime_archive']])]; XF=int(2.5*SR)
# Laurin 16.11.: vor jedem Musikwechsel (= Kapitel) Musik ausblenden, kurze Stille, neuer Track setzt mit der Kapitelkarte ein
FO=int(2.2*SR); GAP=int(0.5*SR); FI=int(1.2*SR)
for i,(t0,name) in enumerate(cues):
    t1 = cues[i+1][0] if i+1<len(cues) else total
    a=int(t0*SR)+(int(0.55*SR) if i>0 else 0); b=min(N,int(t1*SR)-(GAP if i+1<len(cues) else 0)); tr=load_track(name)
    if b<=a: continue
    seg=np.concatenate([tr]*(1+(b-a)//len(tr)))[:b-a].copy()
    ramp=min(FI,len(seg)); seg[:ramp]*=np.linspace(0,1,ramp)[:,None]
    if i+1<len(cues): k=min(FO,len(seg)); seg[-k:]*=np.linspace(1,0,k)[:,None]
    bed[a:a+len(seg)]+=seg
env=np.ones(N,np.float32)
for d0,d1 in m2.get('dips',[]):
    a=int(d0*SR); b=int(d1*SR); r=int(0.25*SR)
    env[a:b]=0.12; env[max(0,a-r):a]=np.minimum(env[max(0,a-r):a],np.linspace(1,0.12,a-max(0,a-r)))
    env[b:b+r]=np.minimum(env[b:b+r],np.linspace(0.12,1,len(env[b:b+r])))
for d0,d1 in m2.get('rests',[]):   # bewusste Musikpausen (Spannung)
    a=int(d0*SR); b=min(N,int(d1*SR)); r=int(0.8*SR)
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
print(len(ev),'sfx',total)
