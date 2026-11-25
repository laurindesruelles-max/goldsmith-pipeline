"""Echten Clip (Pixabay/Archiv) in die Akten-Welt setzen: Clip läuft in einem angepinnten Polaroid auf der Pinnwand
(langsamer Kamera-Drift, Wärme-Grade, Korn). Laurin 22.11.2026: echte Clips immer in der Akten-Welt.
python3 engine/clip_polaroid.py <in.mp4> <out.mp4> <board.png> [max_sek=10] [seed]"""
import sys, subprocess, random
from PIL import Image, ImageDraw, ImageFilter
src, out, board = sys.argv[1:4]; mx = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0; seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rnd = random.Random(seed)
W, H = 1920, 1080; cw, ch = 1280, 720; bx, by, bb = 34, 34, 120          # Clip-Fenster + Polaroid-Ränder
pw, ph = cw+2*bx, ch+by+bb; px = (W-pw)//2 + rnd.randint(-40, 40); py = (H-ph)//2 - 10 + rnd.randint(-15, 15)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([px+14, py+22, px+pw+14, py+ph+22], fill=(0, 0, 0, 170))
ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(ov)
d.rectangle([px, py, px+pw, py+ph], fill=(238, 233, 220, 255))
d.rectangle([px+bx, py+by, px+bx+cw, py+by+ch], fill=(0, 0, 0, 0))
cx = px+pw//2; d.ellipse([cx-16, py-10, cx+16, py+22], fill=(185, 30, 35, 255)); d.ellipse([cx-7, py-3, cx+3, py+7], fill=(240, 120, 120, 255))
ov.save("/tmp/claude-0/polaroid_ov.png")
fc = (f"[0:v]scale=2112:1188,crop=1920:1080:x='96*t/{mx}':y='40*t/{mx}'[bg];"
      f"[1:v]trim=0:{mx},setpts=PTS-STARTPTS,scale={cw}:{ch},eq=saturation=0.82:contrast=1.06,colorbalance=rs=0.05:bs=-0.05[c];"
      f"[bg][c]overlay={px+bx}:{py+by}:shortest=1[a];[a][2:v]overlay=0:0,noise=alls=7:allf=t,vignette=PI/5,format=yuv420p")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-loop", "1", "-i", board, "-i", src, "-loop", "1", "-i", "/tmp/claude-0/polaroid_ov.png",
                "-filter_complex", fc, "-t", str(mx), "-r", "24", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-an", out], check=True)
print("ok", out)
