#!/usr/bin/env bash
# Build EP-002 2D musical cartoon MP4
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EP="$ROOT/ep002_2d"
export PATH="$HOME/.local/bin:$PATH"

echo "=== EP-002 2D render ==="
python3 "$ROOT/scripts/render_ep002_2d.py"

echo "=== FFmpeg mux ==="
ffmpeg -y \
  -framerate 30 \
  -i "$EP/frames/f_%05d.jpg" \
  -i "$EP/audio/bg_music.wav" \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest \
  -movflags +faststart \
  -r 30 \
  -s 1920x1080 \
  "$EP/output/BIP_EP002_COLORS_FINAL.mp4"

echo "=== QA ==="
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,avg_frame_rate,nb_frames -of json \
  "$EP/output/BIP_EP002_COLORS_FINAL.mp4"

python3 - << PY
import json, subprocess, sys
mp4 = "$EP/output/BIP_EP002_COLORS_FINAL.mp4"
info = json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json", mp4], text=True))
fmt = info["format"]; v = next(s for s in info["streams"] if s["codec_type"]=="video")
a = next((s for s in info["streams"] if s["codec_type"]=="audio"), None)
dur = float(fmt["duration"]); w,h = int(v["width"]), int(v["height"])
num,den = v["avg_frame_rate"].split("/"); fps = float(num)/float(den)
ok = True
def check(n,c,d):
    global ok
    print(("PASS" if c else "FAIL"), n, d)
    ok = ok and c
check("duration", abs(dur-100)<1.5, f"{dur:.3f}")
check("res", w==1920 and h==1080, f"{w}x{h}")
check("fps", abs(fps-30)<0.1, str(fps))
check("audio", a is not None, a.get("codec_name") if a else None)
check("h264", v.get("codec_name")=="h264", v.get("codec_name"))
sys.exit(0 if ok else 1)
PY

echo "=== DONE: $EP/output/BIP_EP002_COLORS_FINAL.mp4 ==="
ls -lh "$EP/output/BIP_EP002_COLORS_FINAL.mp4"
