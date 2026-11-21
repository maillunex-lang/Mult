#!/usr/bin/env python3
"""
EP-003 «Бип считает до десяти» — stylish 2D Soft Toy musical cartoon.
Every visual element is generated individually (saved under assets/),
then composed into animated frames. No Godot. No external art packs.

120s · 1920×1080 · 30fps · Russian sung numbers + burned-in subtitles.
"""
from __future__ import annotations

import math
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/workspace/ep003_2d")
ASSETS = ROOT / "assets"
FRAMES = ROOT / "frames"
AUDIO = ROOT / "audio"
OUT = ROOT / "output"

W, H = 1920, 1080
FPS = 30
DURATION = 120.0
TOTAL = int(DURATION * FPS)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Palette — warm preschool cartoon
C = {
    "sky1": (140, 200, 245),
    "sky2": (220, 238, 252),
    "hill1": (110, 190, 105),
    "hill2": (85, 165, 95),
    "hill3": (130, 205, 120),
    "sun": (255, 210, 70),
    "sunglow": (255, 235, 150),
    "cloud": (255, 255, 255),
    "beep": (100, 205, 230),
    "beep2": (70, 180, 210),
    "soft": (250, 252, 255),
    "eye": (30, 35, 48),
    "antenna": (255, 205, 50),
    "blush": (255, 150, 155),
    "wood": (190, 140, 90),
    "shadow": (40, 90, 55),
}

NUM_COLORS = {
    1: (235, 75, 85),
    2: (255, 175, 55),
    3: (90, 160, 240),
    4: (80, 200, 120),
    5: (190, 110, 230),
    6: (255, 120, 160),
    7: (70, 200, 200),
    8: (255, 140, 60),
    9: (120, 140, 255),
    10: (255, 95, 120),
}

NUM_WORDS = {
    1: "Один",
    2: "Два",
    3: "Три",
    4: "Четыре",
    5: "Пять",
    6: "Шесть",
    7: "Семь",
    8: "Восемь",
    9: "Девять",
    10: "Десять",
}

# What Beep counts for each number (cute objects)
COUNT_ITEMS = {
    1: "star",
    2: "heart",
    3: "balloon",
    4: "flower",
    5: "fish",
    6: "apple",
    7: "butterfly",
    8: "candy",
    9: "duck",
    10: "block",
}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def circle(d, xy, r, fill, outline=None, width=1):
    x, y = xy
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline, width=width)


def rounded_rect(d, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------- Individual asset generators ----------

def make_sky() -> Image.Image:
    img = Image.new("RGBA", (W, H))
    px = img.load()
    for y in range(H):
        u = y / (H - 1)
        # soft vertical gradient + slight warm band
        r = int(lerp(C["sky1"][0], C["sky2"][0], u))
        g = int(lerp(C["sky1"][1], C["sky2"][1], u))
        b = int(lerp(C["sky1"][2], C["sky2"][2], u))
        # subtle vignette-ish top left cooler
        for x in range(W):
            px[x, y] = (r, g, b, 255)
    # soft decorative dots (sparkles field)
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for _ in range(40):
        x, y = int(rng.integers(40, W - 40)), int(rng.integers(40, 420))
        rr = int(rng.integers(2, 5))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, 70))
    return img


def make_hills() -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([-400, 720, 1100, 1500], fill=C["hill1"])
    d.ellipse([600, 760, 2300, 1550], fill=C["hill2"])
    d.ellipse([200, 860, 1700, 1600], fill=C["hill3"])
    # grass tufts
    for x in range(80, W, 70):
        y = 940 + (x * 3) % 40
        d.polygon([(x, y), (x + 8, y - 22), (x + 16, y)], fill=(90, 175, 95, 180))
    return img


def make_sun() -> Image.Image:
    size = 420
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size // 2
    for r, a in ((190, 40), (150, 70), (120, 110)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*C["sunglow"], a))
    d.ellipse([cx - 88, cy - 88, cx + 88, cy + 88], fill=C["sun"])
    # cheeks of sun
    d.ellipse([cx - 55, cy + 5, cx - 30, cy + 28], fill=(255, 170, 100, 120))
    d.ellipse([cx + 30, cy + 5, cx + 55, cy + 28], fill=(255, 170, 100, 120))
    # smile
    d.arc([cx - 35, cy - 5, cx + 35, cy + 45], 20, 160, fill=(200, 120, 40), width=5)
    # eyes
    d.ellipse([cx - 38, cy - 25, cx - 18, cy - 5], fill=(80, 60, 40))
    d.ellipse([cx + 18, cy - 25, cx + 38, cy - 5], fill=(80, 60, 40))
    # rays
    for ang in range(0, 360, 20):
        rad = math.radians(ang)
        x1 = cx + math.cos(rad) * 105
        y1 = cy + math.sin(rad) * 105
        x2 = cx + math.cos(rad) * 155
        y2 = cy + math.sin(rad) * 155
        d.line([(x1, y1), (x2, y2)], fill=(*C["sun"], 200), width=10)
    return img


def make_cloud() -> Image.Image:
    img = Image.new("RGBA", (360, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    parts = [(120, 110, 70), (180, 100, 80), (240, 115, 65), (90, 125, 55), (270, 130, 50), (160, 80, 55)]
    for x, y, r in parts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=C["cloud"])
    # soft underside shadow
    d.ellipse([100, 145, 260, 175], fill=(230, 235, 245, 90))
    return img


def make_beep(wave: float = 0.0, blink: float = 0.0, mouth_open: float = 0.0) -> Image.Image:
    """Generate Beep sprite for a given expression (singing-capable mouth)."""
    img = Image.new("RGBA", (420, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 210, 280
    s = 1.0
    # soft body shadow inside sprite
    d.ellipse([cx - 90, cy + 160, cx + 90, cy + 195], fill=(0, 0, 0, 35))
    # feet
    d.ellipse([cx - 70, cy + 130, cx - 20, cy + 175], fill=C["soft"])
    d.ellipse([cx + 20, cy + 130, cx + 70, cy + 175], fill=C["soft"])
    # body
    d.ellipse([cx - 105, cy - 10, cx + 105, cy + 160], fill=C["beep"])
    # belly plate
    d.ellipse([cx - 48, cy + 40, cx + 48, cy + 120], fill=C["soft"])
    # decorative belly dots
    for i, col in enumerate([(255, 120, 120), (255, 200, 80), (100, 180, 255)]):
        d.ellipse([cx - 28 + i * 22, cy + 70, cx - 16 + i * 22, cy + 82], fill=col)
    # head
    d.ellipse([cx - 95, cy - 150, cx + 95, cy + 20], fill=C["beep"])
    # antenna
    d.line([(cx, cy - 145), (cx, cy - 210)], fill=C["antenna"], width=10)
    d.ellipse([cx - 18, cy - 235, cx + 18, cy - 199], fill=C["antenna"])
    # arms
    ay = cy + 30 - wave * 50
    d.ellipse([cx - 155, ay - 30, cx - 95, ay + 30], fill=C["soft"])
    d.ellipse([cx + 95, ay - 20 + wave * 15, cx + 155, ay + 40 + wave * 15], fill=C["soft"])
    # eyes
    eye_h = max(0.12, 1.0 - blink)
    for ex in (-34, 34):
        ew, eh = 26, 26 * eye_h
        d.ellipse([cx + ex - ew, cy - 80 - eh, cx + ex + ew, cy - 80 + eh], fill=C["soft"])
        if eye_h > 0.3:
            d.ellipse([cx + ex - 12, cy - 92, cx + ex + 12, cy - 68], fill=C["eye"])
            d.ellipse([cx + ex - 7, cy - 95, cx + ex - 1, cy - 89], fill=(255, 255, 255))
    # blush
    d.ellipse([cx - 70, cy - 45, cx - 45, cy - 22], fill=(*C["blush"], 160))
    d.ellipse([cx + 45, cy - 45, cx + 70, cy - 22], fill=(*C["blush"], 160))
    # mouth — closed smile or open singing oval
    if mouth_open > 0.25:
        oh = 10 + mouth_open * 22
        ow = 18 + mouth_open * 10
        d.ellipse([cx - ow, cy - 25, cx + ow, cy - 25 + oh], fill=(60, 30, 40))
        # little tongue
        d.ellipse([cx - 8, cy - 12, cx + 8, cy - 2], fill=(255, 120, 130))
    else:
        d.arc([cx - 22, cy - 30, cx + 22, cy - 2], 15, 165, fill=C["eye"], width=5)
    return img


def make_number_badge(n: int) -> Image.Image:
    """Big friendly number badge — each number unique color/shape accent."""
    size = 360
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = NUM_COLORS[n]
    cx = cy = size // 2
    # outer ring
    d.ellipse([20, 20, size - 20, size - 20], fill=(*col, 255))
    d.ellipse([48, 48, size - 48, size - 48], fill=(255, 255, 255, 245))
    # accent petals depending on n
    for i in range(n if n < 8 else 8):
        ang = math.radians(i * (360 / max(n, 1)) - 90)
        px = cx + math.cos(ang) * 145
        py = cy + math.sin(ang) * 145
        d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(*col, 200))
    font = ImageFont.truetype(FONT, 160 if n < 10 else 120)
    text = str(n)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2, (size - th) / 2 - 12), text, font=font, fill=col)
    return img


def make_item(kind: str) -> Image.Image:
    """Countable object sprites — each type drawn uniquely."""
    img = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = 90

    if kind == "star":
        pts = []
        for i in range(10):
            ang = math.radians(-90 + i * 36)
            r = 70 if i % 2 == 0 else 32
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        d.polygon(pts, fill=(255, 210, 60))
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 245, 180))
    elif kind == "heart":
        d.ellipse([cx - 55, cy - 45, cx - 5, cy + 10], fill=(240, 80, 110))
        d.ellipse([cx + 5, cy - 45, cx + 55, cy + 10], fill=(240, 80, 110))
        d.polygon([(cx - 58, cy - 5), (cx + 58, cy - 5), (cx, cy + 60)], fill=(240, 80, 110))
    elif kind == "balloon":
        d.ellipse([cx - 45, cy - 70, cx + 45, cy + 25], fill=(90, 160, 245))
        d.ellipse([cx - 20, cy - 55, cx - 5, cy - 40], fill=(255, 255, 255, 160))
        d.line([(cx, cy + 25), (cx, cy + 75)], fill=(120, 100, 80), width=3)
        d.polygon([(cx - 8, cy + 25), (cx + 8, cy + 25), (cx, cy + 38)], fill=(70, 130, 210))
    elif kind == "flower":
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            px = cx + math.cos(rad) * 35
            py = cy + math.sin(rad) * 35
            d.ellipse([px - 22, py - 22, px + 22, py + 22], fill=(255, 150, 190))
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 220, 70))
        d.line([(cx, cy + 20), (cx, cy + 75)], fill=(80, 170, 90), width=5)
    elif kind == "fish":
        d.ellipse([cx - 55, cy - 30, cx + 35, cy + 30], fill=(90, 190, 220))
        d.polygon([(cx + 30, cy), (cx + 70, cy - 28), (cx + 70, cy + 28)], fill=(70, 160, 200))
        d.ellipse([cx - 30, cy - 12, cx - 12, cy + 6], fill=(30, 40, 50))
        d.ellipse([cx - 26, cy - 10, cx - 20, cy - 4], fill=(255, 255, 255))
    elif kind == "apple":
        d.ellipse([cx - 45, cy - 35, cx + 45, cy + 50], fill=(220, 70, 70))
        d.ellipse([cx - 25, cy - 25, cx - 5, cy - 5], fill=(255, 180, 180, 120))
        d.line([(cx, cy - 35), (cx + 5, cy - 60)], fill=(110, 70, 40), width=4)
        d.ellipse([cx + 2, cy - 70, cx + 35, cy - 45], fill=(90, 180, 90))
    elif kind == "butterfly":
        d.ellipse([cx - 60, cy - 35, cx - 5, cy + 25], fill=(190, 130, 255))
        d.ellipse([cx + 5, cy - 35, cx + 60, cy + 25], fill=(190, 130, 255))
        d.ellipse([cx - 50, cy - 5, cx - 10, cy + 40], fill=(255, 170, 220))
        d.ellipse([cx + 10, cy - 5, cx + 50, cy + 40], fill=(255, 170, 220))
        d.ellipse([cx - 8, cy - 25, cx + 8, cy + 35], fill=(60, 50, 40))
    elif kind == "candy":
        d.ellipse([cx - 35, cy - 25, cx + 35, cy + 25], fill=(255, 120, 160))
        d.polygon([(cx - 35, cy), (cx - 70, cy - 30), (cx - 70, cy + 30)], fill=(120, 200, 255))
        d.polygon([(cx + 35, cy), (cx + 70, cy - 30), (cx + 70, cy + 30)], fill=(120, 200, 255))
        d.ellipse([cx - 12, cy - 10, cx + 12, cy + 10], fill=(255, 220, 80))
    elif kind == "duck":
        d.ellipse([cx - 45, cy - 20, cx + 45, cy + 40], fill=(255, 215, 70))
        d.ellipse([cx + 15, cy - 50, cx + 65, cy], fill=(255, 215, 70))
        d.polygon([(cx + 60, cy - 30), (cx + 90, cy - 22), (cx + 60, cy - 12)], fill=(255, 140, 50))
        d.ellipse([cx + 35, cy - 38, cx + 48, cy - 25], fill=(40, 40, 40))
    else:  # block
        colors = [(240, 90, 90), (90, 160, 240), (255, 200, 60), (90, 200, 120)]
        col = colors[hash(kind) % 4]
        d.rounded_rectangle([cx - 40, cy - 40, cx + 40, cy + 40], radius=12, fill=col)
        d.rounded_rectangle([cx - 28, cy - 28, cx + 28, cy + 28], radius=8, fill=(255, 255, 255, 80))
    return img


def make_stage_banner() -> Image.Image:
    img = Image.new("RGBA", (900, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded_rect(d, [0, 0, 899, 139], 40, (255, 255, 255, 230))
    # colorful dots
    for i, col in enumerate([(240, 90, 90), (255, 180, 60), (90, 170, 240), (90, 200, 120), (190, 120, 230)]):
        d.ellipse([40 + i * 40, 55, 65 + i * 40, 80], fill=col)
        d.ellipse([900 - 70 - i * 40, 55, 900 - 45 - i * 40, 80], fill=col)
    return img


def generate_all_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Generating individual assets...")
    make_sky().save(ASSETS / "bg_sky.png")
    make_hills().save(ASSETS / "bg_hills.png")
    make_sun().save(ASSETS / "sun.png")
    make_cloud().save(ASSETS / "cloud.png")
    make_stage_banner().save(ASSETS / "banner.png")
    for wave in (0.0, 0.5, 1.0):
        make_beep(wave=wave, mouth_open=0.0).save(ASSETS / f"beep_wave_{int(wave*10):02d}.png")
    for mo in (0.0, 0.4, 0.8):
        make_beep(wave=0.3, mouth_open=mo).save(ASSETS / f"beep_sing_{int(mo*10):02d}.png")
    make_beep(blink=1.0).save(ASSETS / "beep_blink.png")
    for n in range(1, 11):
        make_number_badge(n).save(ASSETS / f"number_{n:02d}.png")
    for kind in sorted(set(COUNT_ITEMS.values())):
        make_item(kind).save(ASSETS / f"item_{kind}.png")
    print("Assets ready:", len(list(ASSETS.glob('*.png'))))


# ---------- Timeline / composition ----------

def number_window(n: int):
    """Return (start, end) seconds for number n (1..10)."""
    intro = 10.0
    per = 9.0
    start = intro + (n - 1) * per
    return start, start + per


def subtitle_at(t: float) -> str:
    if t < 9.5:
        return "Бип считает до десяти"
    if t >= 110:
        return "Ура! От одного до десяти!"
    if t >= 100:
        return "Молодец, Бип!"
    for n in range(1, 11):
        a, b = number_window(n)
        if a <= t < b:
            # first half: word, second: digit emphasis
            mid = a + 4.0
            if t < mid:
                return f"{NUM_WORDS[n]}!"
            return f"{n}"
    return ""


def scene_state(t: float):
    """High-level scene mode and active number."""
    if t < 10:
        return "intro", 0
    if t >= 100:
        return "finale", 10
    for n in range(1, 11):
        a, b = number_window(n)
        if a <= t < b:
            return "count", n
    return "finale", 10


def blit(base: Image.Image, sprite: Image.Image, xy, scale=1.0, rotate=0.0):
    if scale != 1.0:
        nw = max(1, int(sprite.width * scale))
        nh = max(1, int(sprite.height * scale))
        sprite = sprite.resize((nw, nh), Image.Resampling.LANCZOS)
    if rotate:
        sprite = sprite.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)
    x, y = xy
    base.alpha_composite(sprite, (int(x - sprite.width / 2), int(y - sprite.height / 2)))


# Cache loaded assets in worker via global after fork init
_AS = {}


def _load_assets():
    global _AS
    if _AS:
        return _AS
    for p in ASSETS.glob("*.png"):
        _AS[p.stem] = Image.open(p).convert("RGBA")
    return _AS


def render_frame(i: int) -> Image.Image:
    A = _load_assets()
    t = i / FPS
    mode, num = scene_state(t)

    img = A["bg_sky"].copy()
    # drifting clouds
    blit(img, A["cloud"], (380 + math.sin(t * 0.25) * 40, 180), scale=1.0)
    blit(img, A["cloud"], (1250 + math.cos(t * 0.2) * 50, 140), scale=0.75)
    # sun
    sun_rot = (t * 6) % 360
    blit(img, A["sun"], (1620, 170), scale=0.85, rotate=sun_rot * 0.15)
    # hills
    img.alpha_composite(A["bg_hills"])

    # Beep expression
    sing_phase = abs(math.sin(t * 8.0))
    blink = 1.0 if (t % 3.6) > 3.4 else 0.0
    if blink > 0:
        beep = A["beep_blink"]
    elif mode == "count" or mode == "finale":
        key = "beep_sing_08" if sing_phase > 0.55 else ("beep_sing_04" if sing_phase > 0.25 else "beep_sing_00")
        beep = A.get(key, A["beep_wave_05"])
    else:
        wave = abs(math.sin(t * 3.5))
        beep = A["beep_wave_10"] if wave > 0.6 else A["beep_wave_05"]

    if mode == "intro":
        u = smooth(t / 10)
        beep_x = lerp(960, 960, u)
        beep_y = lerp(980, 640, u)
        blit(img, A["banner"], (960, 120), scale=1.0)
        font = ImageFont.truetype(FONT, 54)
        d = ImageDraw.Draw(img)
        title = "Бип считает до десяти"
        bbox = d.textbbox((0, 0), title, font=font)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) / 2, 95), title, font=font, fill=(60, 90, 130))
        blit(img, beep, (beep_x, beep_y), scale=1.05)
        # preview tiny numbers flying in
        for n in range(1, 6):
            ang = t * 40 + n * 70
            x = 960 + math.cos(math.radians(ang)) * (180 + n * 30)
            y = 420 + math.sin(math.radians(ang)) * 60
            blit(img, A[f"number_{n:02d}"], (x, y), scale=0.28)

    elif mode == "count":
        a, b = number_window(num)
        local = t - a
        enter = smooth(clamp(local / 1.2))
        # Beep on the left
        blit(img, beep, (420, 640), scale=1.0)
        # Big number badge pops in
        pop = 0.55 + 0.45 * enter
        bounce = abs(math.sin(local * 3.2)) * 18 * enter
        badge_y = 380 - bounce
        blit(img, A[f"number_{num:02d}"], (1280, badge_y), scale=pop)
        # Countable items arc
        kind = COUNT_ITEMS[num]
        item = A[f"item_{kind}"]
        for k in range(num):
            # arrange in arc / row
            if num <= 5:
                ix = 780 + k * 130
                iy = 720
            else:
                row = 0 if k < 5 else 1
                col = k if k < 5 else k - 5
                ix = 780 + col * 130
                iy = 680 + row * 120
            appear = smooth(clamp((local - 0.4 - k * 0.35) / 0.5))
            if appear <= 0:
                continue
            bob = abs(math.sin(t * 4 + k)) * 14
            blit(img, item, (ix, iy - bob), scale=0.55 + 0.35 * appear)

    else:  # finale
        local = t - 100
        blit(img, beep, (960, 620), scale=1.1)
        # all numbers in a rainbow arc
        for n in range(1, 11):
            ang = math.radians(-200 + n * 22)
            radius = 420
            x = 960 + math.cos(ang) * radius
            y = 520 + math.sin(ang) * radius * 0.55
            spin = math.sin(t * 2 + n) * 8
            scale = 0.32 + 0.03 * math.sin(t * 3 + n)
            delay = smooth(clamp((local - n * 0.25) / 0.6))
            if delay > 0:
                blit(img, A[f"number_{n:02d}"], (x, y), scale=scale * delay, rotate=spin)

    # Subtitles
    text = subtitle_at(t)
    if text:
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT, 62)
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 44, 20
        bx = (W - tw) // 2 - pad_x
        by = H - 130
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle(
            [bx, by, bx + tw + pad_x * 2, by + th + pad_y * 2],
            radius=28,
            fill=(35, 45, 65, 200),
        )
        od.text((bx + pad_x, by + pad_y - 2), text, font=font, fill=(255, 255, 255, 255))
        img.alpha_composite(overlay)

    # fade
    fade = 0.0
    if t < 1.0:
        fade = 1.0 - t / 1.0
    if t > DURATION - 3.0:
        fade = (t - (DURATION - 3.0)) / 3.0
    if fade > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * clamp(fade)))))

    return img.convert("RGB")


def _render_one(i: int):
    frame = render_frame(i)
    frame.save(FRAMES / f"f_{i:05d}.jpg", quality=90, optimize=False)


def make_music(path: Path, duration: float):
    sr = 44100
    n = int(sr * duration)
    audio = np.zeros(n, dtype=np.float64)
    t = np.arange(n) / sr
    # soft pad
    for f0, vol in ((130.81, 0.035), (196.0, 0.03), (261.63, 0.025)):
        audio += vol * np.sin(2 * np.pi * f0 * t) * np.linspace(0.7, 1.0, n)

    scale = [261.63, 293.66, 329.63, 349.23, 392.0, 440.0, 493.88, 523.25]
    bpm = 96
    beat = 60.0 / bpm

    def add_tone(f, start, dur, vol=0.11):
        i0 = int(start * sr)
        i1 = min(n, int((start + dur) * sr))
        if i0 >= n:
            return
        tt = np.arange(i1 - i0) / sr
        env = np.ones_like(tt)
        fd = min(len(tt) // 4, int(0.05 * sr))
        if fd > 1:
            env[:fd] = np.linspace(0, 1, fd)
            env[-fd:] = np.linspace(1, 0, fd)
        wave = 0.65 * np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * f * 2 * tt)
        audio[i0:i1] += wave * env * vol

    # cheerful looping motif
    motif = [0, 2, 4, 5, 4, 2, 0, 4, 5, 7, 5, 4, 2, 0, -1, -1]
    t0 = 0.0
    while t0 < duration - 0.5:
        for p in motif:
            if p >= 0:
                add_tone(scale[p % len(scale)], t0, beat * 0.85, 0.09)
            t0 += beat

    # number accent chimes
    for num in range(1, 11):
        a, _ = number_window(num)
        add_tone(scale[(num - 1) % len(scale)], a + 0.3, 0.45, 0.14)
        add_tone(scale[(num - 1) % len(scale)] * 1.5, a + 0.5, 0.35, 0.08)

    fade = int(3 * sr)
    audio[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(audio)) + 1e-9
    audio = audio / peak * 0.75
    import wave, struct
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())


def make_singing_vocals(path: Path):
    """Generate sung-ish Russian number words with gTTS + pitch melody."""
    AUDIO.mkdir(parents=True, exist_ok=True)
    clips = []
    pitches = [0, 2, 4, 5, 7, 5, 4, 2, 0, 4]  # scale degrees for 1..10
    base = 1.0
    for n in range(1, 11):
        word = NUM_WORDS[n]
        raw = AUDIO / f"n{n}_raw.mp3"
        for attempt in range(5):
            try:
                from gtts import gTTS
                gTTS(text=word, lang="ru", slow=False).save(str(raw))
                if raw.stat().st_size > 500:
                    break
            except Exception as e:
                print("tts retry", n, e)
                time.sleep(1.2 * (attempt + 1))
        # melodic pitch via asetrate
        degree = pitches[n - 1]
        rate = 1.0 * (2 ** (degree / 12.0)) * 1.05  # slightly brighter kid tone
        out = AUDIO / f"n{n}.wav"
        tempo = 1.0 / rate
        # keep duration reasonable
        subprocess.check_call([
            "ffmpeg", "-y", "-i", str(raw),
            "-af", f"asetrate=44100*{rate:.4f},aresample=44100,atempo={min(2.0, max(0.5, tempo)):.4f},volume=1.3",
            str(out)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        a, _ = number_window(n)
        clips.append((a + 1.0, out))
        print("vocal", n, word)

    # mix vocals onto silent timeline then return path
    # Build with ffmpeg amix
    # First create silence
    silence = AUDIO / "silence.wav"
    subprocess.check_call([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(DURATION), str(silence)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # overlay each vocal at timestamp using adelay
    filt_parts = []
    inputs = ["-i", str(silence)]
    for idx, (start, clip) in enumerate(clips):
        inputs += ["-i", str(clip)]
        delay_ms = int(start * 1000)
        # adelay needs two channels for stereo but we use mono — use adelay=ms:ms or all=1
        filt_parts.append(f"[{idx+1}]adelay={delay_ms}|{delay_ms},volume=1.15[v{idx}]")
    mix_in = "[0]" + "".join(f"[v{i}]" for i in range(len(clips)))
    filt = ";".join(filt_parts) + f";{mix_in}amix=inputs={len(clips)+1}:normalize=0:dropout_transition=0[out]"
    vocals = path
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", "[out]", "-t", str(DURATION), str(vocals)]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("vocals mixed", vocals)


def write_srt(path: Path):
    cues = [(0.0, 9.5, "Бип считает до десяти")]
    for n in range(1, 11):
        a, b = number_window(n)
        cues.append((a, a + 4.0, f"{NUM_WORDS[n]}!"))
        cues.append((a + 4.0, b, f"{n}"))
    cues.append((100.0, 110.0, "Молодец, Бип!"))
    cues.append((110.0, 119.0, "Ура! От одного до десяти!"))

    def ts(sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int(round((sec - int(sec)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, (a, b, text) in enumerate(cues, 1):
        lines += [str(i), f"{ts(a)} --> {ts(b)}", text, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    FRAMES.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    generate_all_assets()

    for p in FRAMES.glob("f_*.jpg"):
        p.unlink()

    workers = max(1, min(8, (os.cpu_count() or 2)))
    print(f"Rendering {TOTAL} frames with {workers} workers...")
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_render_one, i) for i in range(TOTAL)]
        for fut in as_completed(futs):
            fut.result()
            done += 1
            if done % 400 == 0 or done == TOTAL:
                print(f"  {done}/{TOTAL}")

    print("Music...")
    make_music(AUDIO / "bg_music.wav", DURATION)
    print("Singing vocals...")
    make_singing_vocals(AUDIO / "vocals.wav")
    write_srt(OUT / "BIP_EP003_subtitles.srt")

    # mix music + vocals
    subprocess.check_call([
        "ffmpeg", "-y",
        "-i", str(AUDIO / "bg_music.wav"),
        "-i", str(AUDIO / "vocals.wav"),
        "-filter_complex", "[0]volume=0.55[a0];[1]volume=1.1[a1];[a0][a1]amix=inputs=2:normalize=0[out]",
        "-map", "[out]", str(AUDIO / "master.wav")
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # stills
    for name, idx in (("begin", 120), ("middle", TOTAL // 2), ("end", TOTAL - 120)):
        render_frame(idx).save(OUT / f"still_{name}.png")

    print("DONE")


if __name__ == "__main__":
    main()
