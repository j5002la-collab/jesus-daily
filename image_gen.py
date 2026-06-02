#!/usr/bin/env python3
"""
Generador de imágenes para Jesus Daily.
PNG 1080x1080 con degradados ricos, texto bitmap grande, y crucifijo central.
Sin dependencias externas.
"""

import struct
import zlib
import os
import random
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# ─── 5x7 Bitmap Font (minimal, for basic ASCII + Spanish) ───
BITMAP_FONT = {
    'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'B': [0b11110, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110, 0b00000],
    'C': [0b01110, 0b10001, 0b10000, 0b10000, 0b10001, 0b01110, 0b00000],
    'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110, 0b00000],
    'E': [0b11111, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111, 0b00000],
    'F': [0b11111, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000, 0b00000],
    'G': [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b01110, 0b00000],
    'H': [0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001, 0b00000],
    'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110, 0b00000],
    'J': [0b00111, 0b00001, 0b00001, 0b00001, 0b10001, 0b01110, 0b00000],
    'K': [0b10001, 0b10010, 0b11100, 0b10010, 0b10001, 0b10001, 0b00000],
    'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111, 0b00000],
    'M': [0b10001, 0b11011, 0b10101, 0b10001, 0b10001, 0b10001, 0b00000],
    'N': [0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b00000],
    'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110, 0b00000],
    'P': [0b11110, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000, 0b00000],
    'R': [0b11110, 0b10001, 0b11110, 0b10010, 0b10001, 0b10001, 0b00000],
    'S': [0b01110, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110, 0b00000],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000],
    'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110, 0b00000],
    'V': [0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100, 0b00000],
    'W': [0b10001, 0b10001, 0b10001, 0b10101, 0b11011, 0b10001, 0b00000],
    'X': [0b10001, 0b01010, 0b00100, 0b00100, 0b01010, 0b10001, 0b00000],
    'Y': [0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000],
    'Z': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111, 0b00000],
    '0': [0b01110, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110, 0b00000],
    '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110, 0b00000],
    '2': [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b11111, 0b00000],
    '3': [0b11111, 0b00010, 0b00100, 0b00001, 0b10001, 0b01110, 0b00000],
    '4': [0b00010, 0b00110, 0b01010, 0b11111, 0b00010, 0b00010, 0b00000],
    '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b11110, 0b00000],
    '6': [0b01110, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110, 0b00000],
    '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b00100, 0b00100, 0b00000],
    '8': [0b01110, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110, 0b00000],
    '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110, 0b00000],
    ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '.': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00000],
    ',': [0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b01000, 0b00000],
    ':': [0b00000, 0b00100, 0b00000, 0b00000, 0b00100, 0b00000, 0b00000],
    '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100, 0b00000],
    '?': [0b01110, 0b10001, 0b00010, 0b00100, 0b00000, 0b00100, 0b00000],
    '-': [0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000],
    "'": [0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '"': [0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '(': [0b00010, 0b00100, 0b00100, 0b00100, 0b00100, 0b00010, 0b00000],
    ')': [0b01000, 0b00100, 0b00100, 0b00100, 0b00100, 0b01000, 0b00000],
    '/': [0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000, 0b00000],
    '&': [0b01100, 0b10010, 0b01100, 0b10110, 0b10001, 0b01110, 0b00000],
    '+': [0b00000, 0b00100, 0b01110, 0b00100, 0b00000, 0b00000, 0b00000],
    '@': [0b01110, 0b10001, 0b10111, 0b10101, 0b10000, 0b01110, 0b00000],
    '#': [0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b00000, 0b00000],
    ';': [0b00000, 0b00100, 0b00000, 0b00000, 0b00100, 0b01000, 0b00000],
    'á': [0b00010, 0b00100, 0b01110, 0b10001, 0b11111, 0b10001, 0b10001],
    'é': [0b00010, 0b00100, 0b11111, 0b10000, 0b11110, 0b10000, 0b11111],
    'í': [0b00010, 0b00100, 0b01110, 0b00100, 0b00100, 0b00100, 0b01110],
    'ó': [0b00010, 0b00100, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110],
    'ú': [0b00010, 0b00100, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'ñ': [0b01101, 0b10110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001],
    'Ñ': [0b01101, 0b10110, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001],
    '¡': [0b00100, 0b00000, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    '¿': [0b01110, 0b10001, 0b00010, 0b00100, 0b00000, 0b00100, 0b00000],
    '>': [0b01000, 0b00100, 0b00010, 0b00100, 0b01000, 0b00000, 0b00000],
    '<': [0b00010, 0b00100, 0b01000, 0b00100, 0b00010, 0b00000, 0b00000],
}

# Lowercase = uppercase
for c in list(BITMAP_FONT.keys()):
    if 'a' <= c <= 'z':
        BITMAP_FONT[c] = BITMAP_FONT[c.upper()]


def draw_char(pixels, char, x, y, scale, color, W, H):
    if char not in BITMAP_FONT:
        return
    bitmap = BITMAP_FONT[char]
    r, g, b = color[0], color[1], color[2]
    for row in range(7):
        for col in range(5):
            if bitmap[row] & (1 << (4 - col)):
                for dy in range(scale):
                    for dx in range(scale):
                        px, py = x + col * scale + dx, y + row * scale + dy
                        if 0 <= px < W and 0 <= py < H:
                            offset = 1 + (py * W + px) * 4
                            pixels[offset] = r
                            pixels[offset+1] = g
                            pixels[offset+2] = b


def draw_text(pixels, text, x, y, scale, color, W, H):
    cx = x
    for char in text:
        draw_char(pixels, char, cx, y, scale, color, W, H)
        cx += 6 * scale


def text_width(text, scale):
    return len(text) * 6 * scale


def generate_image(day, post_data):
    """Generate a rich, photo-realistic PNG for Jesus Daily."""
    W, H = 1080, 1080
    random.seed(day * 137 + 42)

    # ── Rich sky-landscape background ──
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter byte
        t = y / H
        for x in range(W):
            h = x / W
            
            if t < 0.45:
                # Sky: deep blue to bright cyan/purple
                r = int(30 + t * 60 + h * 30)
                g = int(20 + t * 80 + h * 20)
                b = int(80 + t * 100 + h * 40)
            elif t < 0.65:
                # Horizon transition: warm oranges/golds
                s = (t - 0.45) / 0.20
                r = int(90 + s * 150 + h * 20)
                g = int(100 + s * 100 - h * 30)
                b = int(180 - s * 140)
            else:
                # Ground: warm earthy tones
                s = (t - 0.65) / 0.35
                r = int(240 - s * 80)
                g = int(200 - s * 80)
                b = int(40 + s * 20)

            # Noise for photographic texture
            noise = (hash(str(x * 3 + y * 7 + day * 13)) % 18) - 9
            r = max(0, min(255, r + noise))
            g = max(0, min(255, g + noise))
            b = max(0, min(255, b + noise))
            
            raw.extend(struct.pack('BBBB', r, g, b, 255))

    # ── Dark overlay band for text readability ──
    # Semi-transparent dark bar at center-bottom
    overlay_start = int(H * 0.30)
    overlay_end = int(H * 0.95)
    for y in range(overlay_start, overlay_end):
        alpha = 0.55
        if y < overlay_start + 80:
            alpha = (y - overlay_start) / 80 * 0.55
        for x in range(int(W * 0.05), int(W * 0.95)):
            offset = 1 + (y * W + x) * 4
            raw[offset] = int(raw[offset] * (1 - alpha))
            raw[offset+1] = int(raw[offset+1] * (1 - alpha))
            raw[offset+2] = int(raw[offset+2] * (1 - alpha))

    # ── Central cross (gold, elegant) ──
    cx, cy = W // 2, int(H * 0.38)
    cross_r, cross_g, cross_b = 0xd4, 0xaf, 0x37  # gold
    
    # Vertical bar
    for dy in range(-80, 81):
        for dx in range(-3, 4):
            px, py = cx + dx, cy + dy
            if 0 <= px < W and 0 <= py < H:
                offset = 1 + (py * W + px) * 4
                raw[offset] = cross_r
                raw[offset+1] = cross_g
                raw[offset+2] = cross_b
    
    # Horizontal bar
    for dy in range(-3, 4):
        for dx in range(-60, 61):
            px, py = cx + dx, cy + dy
            if 0 <= px < W and 0 <= py < H:
                offset = 1 + (py * W + px) * 4
                raw[offset] = cross_r
                raw[offset+1] = cross_g
                raw[offset+2] = cross_b

    # ── TEXT: "JESUS DAILY" at top ──
    title = "JESUS DAILY"
    title_scale = 6
    tw = text_width(title, title_scale)
    draw_text(raw, title, (W - tw) // 2, 60, title_scale, 
             b'\xd4\xaf\x37', W, H)

    # Day counter
    day_text = f"DIA {day}"
    day_scale = 4
    dw = text_width(day_text, day_scale)
    draw_text(raw, day_text, (W - dw) // 2, 130, day_scale,
             b'\xff\xff\xff', W, H)

    # ── Verse (main content, BIG) ──
    verse = post_data.get("verse", "")
    verse_color = b'\xff\xff\xff'
    verse_scale = 5
    font_h = 7 * verse_scale
    max_w = W - 120
    
    words = verse.split()
    lines = []
    cur = ""
    for word in words:
        test = cur + (" " if cur else "") + word
        if text_width(test, verse_scale) < max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    lines = lines[:7]
    
    start_y = int(H * 0.45)
    for i, line in enumerate(lines):
        lw = text_width(line, verse_scale)
        draw_text(raw, line, (W - lw) // 2, start_y + i * (font_h + 16),
                 verse_scale, verse_color, W, H)

    # ── Reference ──
    ref = f"— {post_data.get('reference', '')}"
    ref_scale = 3
    rw = text_width(ref, ref_scale)
    ref_y = start_y + len(lines) * (font_h + 16) + 20
    draw_text(raw, ref, (W - rw) // 2, ref_y, ref_scale,
             b'\xd4\xaf\x37', W, H)

    # ── Reflection (smaller, at bottom) ──
    reflection = post_data.get("reflection", "")
    refl_scale = 2
    refl_max_w = W - 240
    
    refl_words = reflection.split()
    refl_lines = []
    cur = ""
    for word in refl_words:
        test = cur + (" " if cur else "") + word
        if text_width(test, refl_scale) < refl_max_w:
            cur = test
        else:
            if cur:
                refl_lines.append(cur)
            cur = word
    if cur:
        refl_lines.append(cur)
    refl_lines = refl_lines[:4]
    
    refl_start_y = H - 200
    refl_color = b'\xe0\xe0\xe0'
    for i, line in enumerate(refl_lines):
        lw = text_width(line, refl_scale)
        draw_text(raw, line, (W - lw) // 2,
                 refl_start_y + i * (7 * refl_scale + 10),
                 refl_scale, refl_color, W, H)

    # ── Bottom branding ──
    brand = "#JesusDaily  |  youtube.com/@JesusDailyShorts1"
    brand_scale = 2
    bw = text_width(brand, brand_scale)
    draw_text(raw, brand, (W - bw) // 2, H - 60, brand_scale,
             b'\xd4\xaf\x37', W, H)

    # ── PNG Encode ──
    def chunk(ctype, data):
        c = ctype + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw))
    png_data = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

    output_path = IMAGES_DIR / f"dia_{day:03d}.png"
    with open(output_path, 'wb') as f:
        f.write(png_data)

    return output_path


def generate_all():
    import json
    posts_file = BASE_DIR / "posts.json"
    if not posts_file.exists():
        print("❌ posts.json no encontrado")
        return
    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)
    print(f"Generando {len(posts)} imágenes...")
    for post in posts:
        day = post["day"]
        output = IMAGES_DIR / f"dia_{day:03d}.png"
        if output.exists():
            print(f"  ⏭️  Día {day} ya existe")
            continue
        generate_image(day, post)
        print(f"  ✅ Día {day}")
    print("✅ Completo")


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            generate_all()
        else:
            day = int(sys.argv[1])
            posts_file = BASE_DIR / "posts.json"
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
            if 1 <= day <= len(posts):
                post = posts[day - 1]
                path = generate_image(day, post)
                print(f"✅ {path} ({path.stat().st_size // 1024} KB)")
            else:
                print(f"❌ Día {day} fuera de rango (max {len(posts)})")
    else:
        print("Uso: python3 image_gen.py [N|all]")
