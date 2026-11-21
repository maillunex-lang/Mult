#!/usr/bin/env python3
"""
EP-002 2D Soft Toy cartoon: «Бип и цветные шарики»
For toddlers under 2. No voiceover — large Russian subtitles.
1920x1080 @ 30 FPS, ~100 seconds.
"""
from __future__ import annotations

import math
import os
import struct
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/ep002_2d")
FRAMES = ROOT / "frames"
AUDIO = ROOT / "audio"
OUT = ROOT / "output"

W, H = 1920, 1080
FPS = 30
DURATION = 100.0  # seconds
TOTAL = int(DURATION * FPS)

# Soft preschool palette
SKY_TOP = (168, 214, 240)
SKY_BOT = (232, 245, 252)
GRASS = (126, 196, 118)
GRASS_DARK = (98, 168, 92)
SUN = (255, 214, 74)
SUN_GLOW = (255, 236, 160)
CLOUD = (255, 255, 255)
BEEP_BODY = (117, 212, 232)  # #75D4E8
BEEP_SOFT = (245, 250, 252)
BEEP_EYE = (35, 40, 50)
ANTENNA = (255, 210, 55)
BLUSH = (255, 160, 160)
RED = (230, 70, 70)
YELLOW = (245, 200, 50)
BLUE = (80, 150, 230)
GREEN = (70, 190, 120)
SUB_BG = (30, 40, 55, 170)
SUB_FG = (255, 255, 255)
TITLE = (55, 90, 120)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    return smooth(t)


def circle(draw, xy, r, fill, outline=None, width=1):
    x, y = xy
    bbox = [x - r, y - r, x + r, y + r]
    draw.ellipse(bbox, fill=fill, outline=outline, width=width)


def soft_circle(img, xy, r, color, soft=0.35):
    """Draw a soft-edged circle via alpha blob."""
    x, y = xy
    size = int(r * 2.4)
    blob = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob)
    cx = cy = size // 2
    layers = 8
    for i in range(layers, 0, -1):
        rr = r * (i / layers)
        alpha = int(255 * (i / layers) ** 0.5)
        if i < layers * soft:
            alpha = int(alpha * 0.35)
        col = (*color[:3], alpha if len(color) == 3 else color[3])
        # solid core
        if i > layers * 0.55:
            col = (*color[:3], 255)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    # simpler solid soft look
    blob = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color[:3], 255))
    # soft rim
    rim = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.ellipse([cx - r * 1.08, cy - r * 1.08, cx + r * 1.08, cy + r * 1.08], fill=(*color[:3], 60))
    img.alpha_composite(rim, (int(x - size / 2), int(y - size / 2)))
    img.alpha_composite(blob, (int(x - size / 2), int(y - size / 2)))


def gradient_bg(t_sun=1.0):
    img = Image.new("RGBA", (W, H))
    px = img.load()
    # sky gradient
    for y in range(H):
        u = y / (H - 1)
        # morning warmth near sun
        r = int(lerp(SKY_TOP[0], SKY_BOT[0], u))
        g = int(lerp(SKY_TOP[1], SKY_BOT[1], u))
        b = int(lerp(SKY_TOP[2], SKY_BOT[2], u))
        for x in range(W):
            px[x, y] = (r, g, b, 255)
    return img


def draw_ground(img):
    d = ImageDraw.Draw(img)
    # soft hills
    d.ellipse([-200, 780, 900, 1400], fill=GRASS)
    d.ellipse([700, 800, 2100, 1450], fill=GRASS_DARK)
    d.rectangle([0, 920, W, H], fill=GRASS)


def draw_sun(img, t):
    # gentle pulse
    pulse = 1.0 + 0.03 * math.sin(t * 1.5)
    x, y = 1580, 180
    r = 95 * pulse
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i, alpha in ((180, 35), (140, 55), (110, 90)):
        gd.ellipse([x - i, y - i, x + i, y + i], fill=(*SUN_GLOW, alpha))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    circle(d, (x, y), r, SUN)
    # soft rays
    for ang in range(0, 360, 30):
        rad = math.radians(ang + t * 8)
        x1 = x + math.cos(rad) * (r + 18)
        y1 = y + math.sin(rad) * (r + 18)
        x2 = x + math.cos(rad) * (r + 55)
        y2 = y + math.sin(rad) * (r + 55)
        d.line([(x1, y1), (x2, y2)], fill=(*SUN, 180), width=8)


def draw_cloud(img, x, y, scale=1.0, drift=0.0):
    d = ImageDraw.Draw(img)
    x = x + drift
    parts = [
        (0, 0, 70),
        (55, 10, 55),
        (-50, 15, 50),
        (20, -25, 48),
        (-25, -15, 42),
    ]
    for dx, dy, rr in parts:
        circle(d, (x + dx * scale, y + dy * scale), rr * scale, CLOUD)


def draw_beep(img, x, y, scale=1.0, wave=0.0, blink=0.0, happy=0.0):
    d = ImageDraw.Draw(img)
    s = scale
    # shadow
    d.ellipse([x - 70 * s, y + 95 * s, x + 70 * s, y + 120 * s], fill=(70, 120, 80, 60))
    # legs
    circle(d, (x - 28 * s, y + 78 * s), 22 * s, BEEP_SOFT)
    circle(d, (x + 28 * s, y + 78 * s), 22 * s, BEEP_SOFT)
    # body
    circle(d, (x, y + 25 * s), 70 * s, BEEP_BODY)
    # belly
    circle(d, (x, y + 35 * s), 28 * s, BEEP_SOFT)
    # head
    circle(d, (x, y - 55 * s), 62 * s, BEEP_BODY)
    # antenna
    d.line([(x, y - 110 * s), (x, y - 145 * s)], fill=ANTENNA, width=max(4, int(8 * s)))
    circle(d, (x, y - 155 * s), 14 * s, ANTENNA)
    # arms
    arm_y = y + 10 * s - wave * 35 * s
    arm_x_off = 78 * s
    circle(d, (x - arm_x_off, arm_y), 24 * s, BEEP_SOFT)
    circle(d, (x + arm_x_off, arm_y + wave * 10 * s), 24 * s, BEEP_SOFT)
    # eyes
    eye_open = 1.0 - blink
    for ex in (-22 * s, 22 * s):
        # white
        ew, eh = 18 * s, 18 * s * max(0.15, eye_open)
        d.ellipse([x + ex - ew, y - 62 * s - eh, x + ex + ew, y - 62 * s + eh], fill=BEEP_SOFT)
        if eye_open > 0.25:
            pr = 9 * s
            circle(d, (x + ex, y - 62 * s), pr, BEEP_EYE)
            circle(d, (x + ex - 3 * s, y - 66 * s), 3.5 * s, (255, 255, 255))
    # blush
    circle(d, (x - 38 * s, y - 40 * s), 8 * s, BLUSH)
    circle(d, (x + 38 * s, y - 40 * s), 8 * s, BLUSH)
    # smile
    smile_w = 16 * s + happy * 8 * s
    d.arc(
        [x - smile_w, y - 40 * s, x + smile_w, y - 18 * s],
        start=20,
        end=160,
        fill=BEEP_EYE,
        width=max(3, int(5 * s)),
    )


def draw_ball(img, x, y, r, color, bounce=0.0):
    d = ImageDraw.Draw(img)
    yy = y - abs(bounce)
    # shadow
    squash = 1.0 + min(0.35, abs(bounce) / 80.0)
    d.ellipse([x - r * squash, y + r * 0.7, x + r * squash, y + r * 1.05], fill=(60, 110, 70, 55))
    circle(d, (x, yy), r, color)
    # highlight
    circle(d, (x - r * 0.28, yy - r * 0.28), r * 0.22, (255, 255, 255, 140))


def draw_subtitle(img, text, font_big, font_small):
    if not text:
        return
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # measure
    bbox = d.textbbox((0, 0), text, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 48, 22
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    bx = (W - box_w) // 2
    by = H - 140
    d.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=28, fill=SUB_BG)
    d.text((bx + pad_x, by + pad_y - 2), text, font=font_big, fill=SUB_FG)
    img.alpha_composite(overlay)


def subtitle_at(t: float) -> str:
    # Slow, clear captions for under-2s
    cues = [
        (0.0, 7.5, "Бип и цветные шарики"),
        (8.0, 16.0, "Привет!"),
        (17.0, 30.0, "Красный шарик"),
        (31.0, 44.0, "Жёлтый шарик"),
        (45.0, 58.0, "Синий шарик"),
        (59.0, 72.0, "Зелёный шарик"),
        (73.0, 86.0, "Раз… два… три… четыре!"),
        (87.0, 99.0, "Пока-пока!"),
    ]
    for a, b, s in cues:
        if a <= t < b:
            return s
    return ""


def scene_params(t: float):
    """Return animation state for time t."""
    # Beep position/actions
    beep_x, beep_y = 960, 620
    wave = 0.0
    blink = 0.0
    happy = 0.0
    balls = []  # list of dicts

    # blink every ~3.5s
    phase = t % 3.5
    if phase > 3.25:
        blink = smooth((phase - 3.25) / 0.12)
        if phase > 3.37:
            blink = 1.0 - smooth((phase - 3.37) / 0.12)

    if t < 8:
        # intro: beep slides in
        u = ease_in_out(t / 8)
        beep_x = lerp(960, 960, u)
        beep_y = lerp(900, 620, u)
        happy = 0.2
    elif t < 17:
        wave = abs(math.sin((t - 8) * 4.0))
        happy = 0.6
    elif t < 31:
        # red ball
        u = ease_in_out(clamp((t - 17) / 3))
        bx = lerp(-120, 560, u)
        by = 720
        bounce = abs(math.sin((t - 17) * 4.2)) * 70 * u
        balls.append({"x": bx, "y": by, "r": 95, "c": RED, "b": bounce})
        beep_x = 1180
        happy = 0.4
        wave = 0.15
    elif t < 45:
        balls.append({"x": 560, "y": 720, "r": 90, "c": RED, "b": abs(math.sin(t * 2)) * 20})
        u = ease_in_out(clamp((t - 31) / 3))
        bx = lerp(2100, 960, u)
        bounce = abs(math.sin((t - 31) * 4.0)) * 70 * u
        balls.append({"x": bx, "y": 700, "r": 95, "c": YELLOW, "b": bounce})
        beep_x = 1280
        happy = 0.5
    elif t < 59:
        balls.append({"x": 480, "y": 730, "r": 85, "c": RED, "b": 10})
        balls.append({"x": 900, "y": 710, "r": 85, "c": YELLOW, "b": 15})
        u = ease_in_out(clamp((t - 45) / 3))
        bx = lerp(-150, 700, u)
        bounce = abs(math.sin((t - 45) * 4.1)) * 70 * u
        balls.append({"x": bx, "y": 690, "r": 95, "c": BLUE, "b": bounce})
        beep_x = 1300
        happy = 0.55
    elif t < 73:
        balls.append({"x": 420, "y": 735, "r": 80, "c": RED, "b": 8})
        balls.append({"x": 780, "y": 715, "r": 80, "c": YELLOW, "b": 12})
        balls.append({"x": 1100, "y": 700, "r": 80, "c": BLUE, "b": 10})
        u = ease_in_out(clamp((t - 59) / 3))
        bx = lerp(2100, 1450, u)
        bounce = abs(math.sin((t - 59) * 4.0)) * 70 * u
        balls.append({"x": bx, "y": 705, "r": 95, "c": GREEN, "b": bounce})
        beep_x = 960
        beep_y = 560
        happy = 0.7
        wave = 0.2
    elif t < 87:
        # all bounce together, count
        cols = [RED, YELLOW, BLUE, GREEN]
        xs = [420, 780, 1140, 1500]
        for i, (cx, col) in enumerate(zip(xs, cols)):
            bounce = abs(math.sin(t * 3.2 + i * 0.7)) * 90
            balls.append({"x": cx, "y": 720, "r": 88, "c": col, "b": bounce})
        beep_x = 960
        beep_y = 540
        wave = abs(math.sin(t * 5.0))
        happy = 1.0
    else:
        # goodbye
        cols = [RED, YELLOW, BLUE, GREEN]
        xs = [500, 820, 1140, 1460]
        for i, (cx, col) in enumerate(zip(xs, cols)):
            bounce = abs(math.sin(t * 2.0 + i)) * 25
            balls.append({"x": cx, "y": 740, "r": 70, "c": col, "b": bounce})
        beep_x = 960
        wave = abs(math.sin((t - 87) * 4.5))
        happy = 0.8

    return beep_x, beep_y, wave, blink, happy, balls


def render_frame(i: int, font_big, font_title):
    t = i / FPS
    img = gradient_bg()
    draw_ground(img)
    draw_sun(img, t)
    draw_cloud(img, 320, 210, 1.1, math.sin(t * 0.3) * 30)
    draw_cloud(img, 1100, 160, 0.85, math.sin(t * 0.25 + 1) * 40)

    beep_x, beep_y, wave, blink, happy, balls = scene_params(t)

    # title card overlay early
    if t < 7.5:
        d = ImageDraw.Draw(img)
        title = "Бип и цветные шарики"
        bbox = d.textbbox((0, 0), title, font=font_title)
        tw = bbox[2] - bbox[0]
        alpha = int(255 * clamp(1.0 if t > 1 else t / 1.0) * clamp((7.5 - t) / 0.8))
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle(
            [(W - tw) // 2 - 50, 80, (W + tw) // 2 + 50, 180],
            radius=30,
            fill=(255, 255, 255, min(220, alpha)),
        )
        od.text(((W - tw) // 2, 100), title, font=font_title, fill=(*TITLE, alpha))
        img.alpha_composite(overlay)

    # draw balls behind / around beep depending on x
    behind = [b for b in balls if b["x"] <= beep_x]
    front = [b for b in balls if b["x"] > beep_x]
    for b in behind:
        draw_ball(img, b["x"], b["y"], b["r"], b["c"], b["b"])
    draw_beep(img, beep_x, beep_y, scale=1.15, wave=wave, blink=blink, happy=happy)
    for b in front:
        draw_ball(img, b["x"], b["y"], b["r"], b["c"], b["b"])

    draw_subtitle(img, subtitle_at(t), font_big, font_big)

    # fade in/out
    fade = 0.0
    if t < 1.2:
        fade = 1.0 - t / 1.2
    if t > DURATION - 3.0:
        fade = (t - (DURATION - 3.0)) / 3.0
    if fade > 0:
        black = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * clamp(fade))))
        img.alpha_composite(black)

    return img.convert("RGB")


def make_music(path: Path, duration: float):
    """Soft lullaby-like loop for toddlers (original)."""
    sr = 44100
    n = int(sr * duration)
    t = np.arange(n) / sr
    # pentatonic soft melody
    scale = np.array([261.63, 293.66, 329.63, 392.00, 440.00, 523.25])
    pattern = [0, 2, 4, 2, 3, 1, 0, 2, 4, 5, 4, 3, 2, 0, -1, -1]
    bpm = 72
    beat = 60.0 / bpm
    audio = np.zeros(n, dtype=np.float64)

    def tone(f, start, dur, vol=0.12):
        i0 = int(start * sr)
        i1 = min(n, int((start + dur) * sr))
        if i0 >= n:
            return
        tt = np.arange(i1 - i0) / sr
        env = np.ones_like(tt)
        fade = int(0.04 * sr)
        if len(env) > 2 * fade:
            env[:fade] = np.linspace(0, 1, fade)
            env[-fade:] = np.linspace(1, 0, fade)
        wave = 0.7 * np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * f * 2 * tt)
        audio[i0:i1] += wave * env * vol

    # pad
    for f0 in (130.81, 196.00, 261.63):
        tone(f0, 0, duration, vol=0.03)

    t0 = 0.0
    while t0 < duration - 0.5:
        for p in pattern:
            if p >= 0:
                tone(scale[p], t0, beat * 0.9, vol=0.10)
            t0 += beat
            if t0 >= duration:
                break

    # gentle chimes on color moments
    for mark, f in ((18, 523), (32, 587), (46, 659), (60, 698), (74, 784)):
        tone(f, mark, 0.5, vol=0.11)
        tone(f * 1.5, mark + 0.15, 0.4, vol=0.06)

    # fade out
    fade = int(3 * sr)
    audio[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(audio)) + 1e-9
    audio = audio / peak * 0.85
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())


def write_srt(path: Path):
    cues = [
        (0.0, 7.5, "Бип и цветные шарики"),
        (8.0, 16.0, "Привет!"),
        (17.0, 30.0, "Красный шарик"),
        (31.0, 44.0, "Жёлтый шарик"),
        (45.0, 58.0, "Синий шарик"),
        (59.0, 72.0, "Зелёный шарик"),
        (73.0, 86.0, "Раз… два… три… четыре!"),
        (87.0, 99.0, "Пока-пока!"),
    ]

    def ts(sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int((sec - int(sec)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, (a, b, text) in enumerate(cues, 1):
        lines += [str(i), f"{ts(a)} --> {ts(b)}", text, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def _render_one(i: int) -> None:
    font_big = ImageFont.truetype(FONT_PATH, 64)
    font_title = ImageFont.truetype(FONT_PATH, 72)
    frame = render_frame(i, font_big, font_title)
    frame.save(FRAMES / f"f_{i:05d}.jpg", quality=90, optimize=False)


def main():
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import os as _os

    FRAMES.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    # clean old frames
    for p in FRAMES.glob("f_*.jpg"):
        p.unlink()

    workers = max(1, min(8, (_os.cpu_count() or 2)))
    print(f"Rendering {TOTAL} frames ({DURATION}s @ {FPS}fps) with {workers} workers...")
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_render_one, i) for i in range(TOTAL)]
        for fut in as_completed(futs):
            fut.result()
            done += 1
            if done % 300 == 0 or done == TOTAL:
                print(f"  {done}/{TOTAL}")

    music = AUDIO / "bg_music.wav"
    print("Composing music...")
    make_music(music, DURATION)
    srt = OUT / "BIP_EP002_subtitles.srt"
    write_srt(srt)

    font_big = ImageFont.truetype(FONT_PATH, 64)
    font_title = ImageFont.truetype(FONT_PATH, 72)
    for name, idx in (("begin", 90), ("middle", TOTAL // 2), ("end", TOTAL - 90)):
        render_frame(idx, font_big, font_title).save(OUT / f"still_{name}.png")

    print("DONE frames+music+srt")


if __name__ == "__main__":
    main()
