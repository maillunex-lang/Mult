#!/usr/bin/env bash
# Unified build: Godot Movie Maker -> FFmpeg MP4 -> ffprobe QA
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$ROOT/godot_project"
OUT_DIR="$PROJECT/output"
AUDIO_MASTER="$PROJECT/audio/master_ep001.wav"
GODOT="${GODOT:-godot}"
MODE="${1:-FINAL}" # PREVIEW | FINAL

mkdir -p "$OUT_DIR" "$PROJECT/screenshots"
export PATH="/home/ubuntu:$HOME/.local/bin:$PATH"

if ! command -v "$GODOT" >/dev/null 2>&1; then
  if [[ -x /home/ubuntu/godot ]]; then GODOT=/home/ubuntu/godot
  elif [[ -x /usr/local/bin/godot ]]; then GODOT=/usr/local/bin/godot
  else echo "ERROR: godot not found"; exit 1; fi
fi

echo "=== BIP EP-001 BUILD ($MODE) ==="
echo "Godot: $($GODOT --version 2>/dev/null || true)"

# Configure mode via project override
if [[ "$MODE" == "PREVIEW" ]]; then
  WIDTH=1280
  HEIGHT=720
  EP_SECONDS=12
  FRAMES=360
  FINAL_MP4="$OUT_DIR/BIP_EP001_PREVIEW.mp4"
  RAW="$OUT_DIR/raw_preview.avi"
  USER_ARGS="-- --preview"
else
  WIDTH=1920
  HEIGHT=1080
  EP_SECONDS=180
  FRAMES=5400
  FINAL_MP4="$OUT_DIR/BIP_EP001_FINAL.mp4"
  RAW="$OUT_DIR/raw_final.avi"
  USER_ARGS=""
fi

# Ensure project setting for movie writer destination
python3 - << PY
from pathlib import Path
p = Path("$PROJECT/project.godot")
text = p.read_text()
# Force movie file path for this run via override cfg
Path("$PROJECT/override.cfg").write_text("""
[editor]
movie_writer/movie_file=\"$RAW\"
movie_writer/fps=30
movie_writer/mjpeg_quality=0.85

[display]
window/size/viewport_width=$WIDTH
window/size/viewport_height=$HEIGHT

[bip]
render/mode=\"$MODE\"
""")
print("override.cfg written")
PY

# Import resources (first run)
echo "[1/4] Importing Godot resources..."
$GODOT --headless --path "$PROJECT" --import --quit-after 120 2>&1 | tee "$OUT_DIR/import.log" | tail -30

# Movie Maker render (deterministic fixed FPS)
echo "[2/4] Rendering with Godot Movie Maker ($FRAMES frames @ 30fps)..."
# --write-movie enables Movie Maker; --fixed-fps locks simulation
set +e
$GODOT --path "$PROJECT" \
  --write-movie "$RAW" \
  --fixed-fps 30 \
  --quit-after "$FRAMES" \
  --resolution "${WIDTH}x${HEIGHT}" \
  $USER_ARGS \
  2>&1 | tee "$OUT_DIR/render.log"
RENDER_EC=${PIPESTATUS[0]}
set -e
echo "Render exit code: $RENDER_EC"

if [[ ! -f "$RAW" ]]; then
  # Sometimes Godot writes relative to project
  if [[ -f "$PROJECT/raw_movie.avi" ]]; then
    mv "$PROJECT/raw_movie.avi" "$RAW"
  elif [[ -f "$PROJECT/output/raw_movie.avi" ]]; then
    mv "$PROJECT/output/raw_movie.avi" "$RAW"
  else
    echo "ERROR: Movie Maker output not found"
    ls -la "$OUT_DIR" || true
    find "$PROJECT" -name '*.avi' -o -name '*.png' 2>/dev/null | head
    exit 2
  fi
fi

echo "[3/4] Muxing audio with FFmpeg..."
if [[ ! -f "$AUDIO_MASTER" ]]; then
  echo "ERROR: missing master audio $AUDIO_MASTER"; exit 3
fi

# Cut audio to mode length for preview
AUDIO_IN="$AUDIO_MASTER"
if [[ "$MODE" == "PREVIEW" ]]; then
  AUDIO_IN="$OUT_DIR/preview_audio.wav"
  ffmpeg -y -i "$AUDIO_MASTER" -t "$EP_SECONDS" "$AUDIO_IN" 2>/dev/null
fi

ffmpeg -y \
  -i "$RAW" \
  -i "$AUDIO_IN" \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest \
  -movflags +faststart \
  -r 30 \
  -s "${WIDTH}x${HEIGHT}" \
  "$FINAL_MP4" 2>&1 | tee "$OUT_DIR/ffmpeg.log" | tail -20

echo "[4/4] QA via ffprobe..."
python3 - << PY
import json, subprocess, sys
mp4 = "$FINAL_MP4"
mode = "$MODE"
expect_dur = float("$EP_SECONDS")
expect_w = int("$WIDTH")
expect_h = int("$HEIGHT")
js = subprocess.check_output([
  "ffprobe","-v","error","-show_streams","-show_format","-of","json", mp4
], text=True)
info = json.loads(js)
fmt = info["format"]
streams = info["streams"]
v = next(s for s in streams if s["codec_type"]=="video")
a = next((s for s in streams if s["codec_type"]=="audio"), None)
dur = float(fmt.get("duration", 0))
w = int(v.get("width",0)); h=int(v.get("height",0))
# avg_frame_rate like 30/1
fr = v.get("avg_frame_rate","0/1")
num,den = fr.split("/")
fps = float(num)/float(den) if float(den) else 0
ok = True
def check(name, cond, detail):
    global ok
    status = "PASS" if cond else "FAIL"
    if not cond: ok=False
    print(f"  [{status}] {name}: {detail}")
print("QA Report:")
check("file_exists", True, mp4)
check("duration", abs(dur-expect_dur)<=1.5, f"{dur:.3f}s (expect ~{expect_dur})")
check("resolution", w==expect_w and h==expect_h, f"{w}x{h}")
check("fps", abs(fps-30)<0.5, f"{fps}")
check("has_audio", a is not None, a.get("codec_name") if a else "missing")
check("video_codec", v.get("codec_name")=="h264", v.get("codec_name"))
if a:
    check("audio_codec", a.get("codec_name") in ("aac","mp3"), a.get("codec_name"))
# rough frame count
nb = v.get("nb_frames")
if nb and nb.isdigit():
    expect_frames = int(expect_dur*30)
    check("frame_count", abs(int(nb)-expect_frames)<=45, f"{nb} (expect ~{expect_frames})")
sys.exit(0 if ok else 10)
PY

echo "=== DONE: $FINAL_MP4 ==="
ls -lh "$FINAL_MP4"
