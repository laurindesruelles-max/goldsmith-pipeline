import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=1)
out = {}
for i in range(1, 10):
    segs, _ = m.transcribe(__import__("numpy").fromfile(f"/home/claude/anom/vo/{i}.f32", dtype="float32"), language="de", word_timestamps=True)
    ws = [(w.word.strip(), round(w.start, 2), round(w.end, 2)) for s in segs for w in s.words]
    out[i] = ws; print(i, " ".join(w[0] for w in ws), ws[-1][2] if ws else None, flush=True)
json.dump(out, open("/home/claude/anom/words.json", "w"), ensure_ascii=False)
