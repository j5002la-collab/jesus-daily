#!/usr/bin/env python3
"""
Generador de imágenes para Global Jesus — Python PURO, sin dependencias.
Estilo heredado de Mensanity: texto bitmap sobre fondo oscuro degradado.
1080x1080 PNG.
"""
import struct
import zlib
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "images"

# ═══════════════════════════════════════════════════════════════
# PNG Writer (pure Python)
# ═══════════════════════════════════════════════════════════════
def create_png(width, height, pixels):
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    raw = bytearray((width * 4 + 1) * height)
    for y in range(height):
        row_start = y * (width * 4 + 1)
        raw[row_start] = 0
        src_start = y * width * 4
        raw[row_start + 1:row_start + 1 + width * 4] = pixels[src_start:src_start + width * 4]

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(bytes(raw))) +
            chunk(b'IEND', b''))

# ═══════════════════════════════════════════════════════════════
# Bitmap Font (5x7, built-in)
# ═══════════════════════════════════════════════════════════════
FONT_DATA = {
    'A':[0b01110,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
    'B':[0b11110,0b10001,0b11110,0b10001,0b10001,0b10001,0b11110],
    'C':[0b01110,0b10001,0b10000,0b10000,0b10000,0b10001,0b01110],
    'D':[0b11110,0b10001,0b10001,0b10001,0b10001,0b10001,0b11110],
    'E':[0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b11111],
    'F':[0b11111,0b10000,0b11110,0b10000,0b10000,0b10000,0b10000],
    'G':[0b01110,0b10001,0b10000,0b10111,0b10001,0b10001,0b01110],
    'H':[0b10001,0b10001,0b11111,0b10001,0b10001,0b10001,0b10001],
    'I':[0b01110,0b00100,0b00100,0b00100,0b00100,0b00100,0b01110],
    'J':[0b00111,0b00001,0b00001,0b00001,0b00001,0b10001,0b01110],
    'K':[0b10001,0b10010,0b11100,0b10000,0b11100,0b10010,0b10001],
    'L':[0b10000,0b10000,0b10000,0b10000,0b10000,0b10000,0b11111],
    'M':[0b10001,0b11011,0b10101,0b10001,0b10001,0b10001,0b10001],
    'N':[0b10001,0b10001,0b11001,0b10101,0b10011,0b10001,0b10001],
    'O':[0b01110,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'P':[0b11110,0b10001,0b10001,0b11110,0b10000,0b10000,0b10000],
    'Q':[0b01110,0b10001,0b10001,0b10001,0b10101,0b10010,0b01101],
    'R':[0b11110,0b10001,0b10001,0b11110,0b10010,0b10001,0b10001],
    'S':[0b01111,0b10000,0b01110,0b00001,0b00001,0b10001,0b01110],
    'T':[0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b00100],
    'U':[0b10001,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'V':[0b10001,0b10001,0b10001,0b10001,0b10001,0b01010,0b00100],
    'W':[0b10001,0b10001,0b10001,0b10101,0b10101,0b11011,0b10001],
    'X':[0b10001,0b10001,0b01010,0b00100,0b01010,0b10001,0b10001],
    'Y':[0b10001,0b10001,0b01010,0b00100,0b00100,0b00100,0b00100],
    'Z':[0b11111,0b00001,0b00010,0b00100,0b01000,0b10000,0b11111],
    '0':[0b01110,0b10001,0b10011,0b10101,0b11001,0b10001,0b01110],
    '1':[0b00100,0b01100,0b00100,0b00100,0b00100,0b00100,0b01110],
    '2':[0b01110,0b10001,0b00001,0b00110,0b01000,0b10000,0b11111],
    '3':[0b01110,0b10001,0b00001,0b00110,0b00001,0b10001,0b01110],
    '4':[0b00010,0b00110,0b01010,0b10010,0b11111,0b00010,0b00010],
    '5':[0b11111,0b10000,0b11110,0b00001,0b00001,0b10001,0b01110],
    '6':[0b01110,0b10001,0b10000,0b11110,0b10001,0b10001,0b01110],
    '7':[0b11111,0b00001,0b00010,0b00100,0b01000,0b01000,0b01000],
    '8':[0b01110,0b10001,0b10001,0b01110,0b10001,0b10001,0b01110],
    '9':[0b01110,0b10001,0b10001,0b01111,0b00001,0b10001,0b01110],
    ' ':[0b00000]*7, '.':[0,0,0,0,0,0,0b00100],
    ',':[0,0,0,0,0,0b00100,0b01000], ':':[0,0,0b00100,0,0,0b00100,0],
    ';':[0,0,0b00100,0,0,0b00100,0b01000], '!':[0b00100]*5+[0,0b00100],
    '?':[0b01110,0b10001,0b00001,0b00110,0b00100,0,0b00100],
    '-':[0]*3+[0b11111]+[0]*3, '—':[0]*3+[0b11111]+[0]*3,
    '\'':[0b00100,0b00100]+[0]*5, '"':[0b01010,0b01010]+[0]*5,
    '(':[0b00010,0b00100,0b01000,0b01000,0b01000,0b00100,0b00010],
    ')':[0b01000,0b00100,0b00010,0b00010,0b00010,0b00100,0b01000],
    '[':[0b01110,0b01000]*3+[0b01110],
    ']':[0b01110,0b00010]*3+[0b01110],
    '¿':[0,0b00100,0,0b00100,0b01000,0b10001,0b01110],
    '¡':[0b00100,0]+[0b00100]*5,
    'á':[0b00010,0b00100,0b01110,0b10001,0b11111,0b10001,0b10001],
    'é':[0b00010,0b00100,0b01110,0b10001,0b11111,0b10000,0b01110],
    'í':[0b00010,0b00100,0b01110,0b00100,0b00100,0b00100,0b01110],
    'ó':[0b00010,0b00100,0b01110,0b10001,0b10001,0b10001,0b01110],
    'ú':[0b00010,0b00100,0b10001,0b10001,0b10001,0b10011,0b01101],
    'ñ':[0,0b01010,0b10100,0b11110,0b10001,0b10001,0b10001],
    'Ñ':[0b01010,0b10100,0b10001,0b11001,0b10101,0b10011,0b10001],
}

def get_char_bitmap(ch):
    if ch in FONT_DATA:
        return FONT_DATA[ch]
    u = ch.upper()
    if u in FONT_DATA:
        return FONT_DATA[u]
    return FONT_DATA[' ']

def draw_text(pixels, width, height, text, x, y, color, scale=1):
    cur_x = x
    for ch in text:
        bm = get_char_bitmap(ch)
        char_w = 5
        for row in range(7):
            for col in range(char_w):
                if (bm[row] >> (char_w - 1 - col)) & 1:
                    for sy in range(scale):
                        for sx in range(scale):
                            px = cur_x + col * scale + sx
                            py = y + row * scale + sy
                            if 0 <= px < width and 0 <= py < height:
                                idx = (py * width + px) * 4
                                pixels[idx:idx+4] = color
        cur_x += (char_w + 1) * scale

def text_width(text, scale=1, spacing=1):
    w = 0
    for ch in text:
        w += (6 if ch != ' ' else 3) + spacing
    return w * scale - spacing

def wrap_text(text, max_chars):
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        if len(word) > max_chars:
            if current:
                lines.append(current.strip())
                current = ''
            for i in range(0, len(word), max_chars):
                lines.append(word[i:i+max_chars])
        elif len(current + ' ' + word) <= max_chars or not current:
            current = (current + ' ' + word).strip()
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# ═══════════════════════════════════════════════════════════════
# Image Generator — estilo Mensanity adaptado a Global Jesus
# ═══════════════════════════════════════════════════════════════
def generate_image(day, verse, reference, reflection, output_path):
    W, H = 1080, 1080
    pixels = bytearray(W * H * 4)

    # Elegant dark gradient background (same as Mensanity)
    for y in range(H):
        t = y / H
        r = int(15 + t * 12)
        g = int(14 + t * 10)
        b = int(20 + t * 14)
        for x in range(W):
            idx = (y * W + x) * 4
            pixels[idx:idx+4] = [r, g, b, 255]

    # Subtle radial glow in center
    cx, cy = W // 2, H // 3
    for y in range(H):
        for x in range(W):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            glow = max(0, int(15 * (1 - dist / 600)))
            if glow > 0:
                idx = (y * W + x) * 4
                pixels[idx] = min(255, pixels[idx] + glow)
                pixels[idx+2] = min(255, pixels[idx+2] + glow // 2)

    # Colors
    white = [225, 225, 230, 255]
    gold = [195, 155, 80, 255]
    dim = [140, 140, 155, 255]
    very_dim = [90, 90, 105, 255]
    accent = [70, 130, 180, 255]   # steel blue for Christian theme

    # Top ornamental line
    for x in range(W//4, 3*W//4):
        for ty in range(2):
            idx = ((55 + ty) * W + x) * 4
            pixels[idx:idx+4] = gold

    # Day badge
    day_text = f"DIA {day}"
    day_scale = 3
    dw = text_width(day_text, day_scale)
    draw_text(pixels, W, H, day_text, (W - dw)//2, 80, gold, day_scale)

    # Decorative cross (Christian motif instead of quotes)
    cross_color = [180, 160, 110, 255]
    cross_y = 170
    for dx in range(-4, 5):
        for dy in range(-18, 19):
            px, py = W//2 + dx, cross_y + dy
            if 0 <= px < W and 0 <= py < H:
                idx = (py * W + px) * 4
                pixels[idx:idx+4] = cross_color
    for dy in range(-4, 5):
        for dx in range(-14, 15):
            px, py = W//2 + dx, cross_y + dy
            if 0 <= px < W and 0 <= py < H:
                idx = (py * W + px) * 4
                pixels[idx:idx+4] = cross_color

    # Verse (main attraction)
    verse_scale = 5 if len(verse) < 60 else 4
    max_chars = 18 if verse_scale == 5 else 22
    lines = wrap_text(verse, max_chars)
    line_h = 7 * verse_scale + 12

    verse_y_start = 240
    for i, line in enumerate(lines):
        lw = text_width(line, verse_scale)
        lx = (W - lw) // 2
        ly = verse_y_start + i * line_h
        draw_text(pixels, W, H, line, lx, ly, white, verse_scale)

    # Reference
    ref_text = f"— {reference}"
    ref_scale = 3
    rw = text_width(ref_text, ref_scale)
    ref_y = verse_y_start + len(lines) * line_h + 45
    draw_text(pixels, W, H, ref_text, (W - rw)//2, ref_y, gold, ref_scale)

    # Separator
    sep_y = ref_y + 55
    for x in range(W//3, 2*W//3):
        idx = (sep_y * W + x) * 4
        pixels[idx:idx+4] = very_dim

    # Reflection (smaller, subtle)
    refl_scale = 2
    refl_lines = wrap_text(reflection, 48)
    refl_line_h = 7 * refl_scale + 6
    refl_y_start = sep_y + 35

    for i, line in enumerate(refl_lines):
        lw = text_width(line, refl_scale)
        lx = (W - lw) // 2
        ly = refl_y_start + i * refl_line_h
        if ly + 14 > H - 80:
            break
        draw_text(pixels, W, H, line, lx, ly, dim, refl_scale)

    # Bottom section: GLOBAL JESUS branding
    brand = "G L O B A L   J E S U S"
    brand_scale = 2
    bw = text_width(brand, brand_scale, spacing=2)
    draw_text(pixels, W, H, brand, (W - bw)//2, H - 60, very_dim, brand_scale)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    png_data = create_png(W, H, pixels)
    with open(output_path, 'wb') as f:
        f.write(png_data)


def generate_all():
    OUTPUT_DIR.mkdir(exist_ok=True)
    posts_file = BASE_DIR / "posts.json"
    if not posts_file.exists():
        print("❌ posts.json no encontrado")
        return

    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print(f"Generando {len(posts)} imágenes...")
    for post in posts:
        day = post["day"]
        path = OUTPUT_DIR / f"dia_{day:03d}.png"
        if path.exists():
            print(f"  ⏭️  Día {day} ya existe")
            continue
        generate_image(
            day=day,
            verse=post["verse"],
            reference=post["reference"],
            reflection=post["reflection"],
            output_path=str(path)
        )
        print(f"  ✅ dia_{day:03d}.png ({path.stat().st_size // 1024} KB)")
    print("✅ Completo")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            generate_all()
        else:
            day = int(sys.argv[1])
            posts_file = BASE_DIR / "posts.json"
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
            post = posts[day - 1]  # day is 1-indexed
            path = OUTPUT_DIR / f"dia_{day:03d}.png"
            generate_image(
                day=day,
                verse=post["verse"],
                reference=post["reference"],
                reflection=post["reflection"],
                output_path=str(path)
            )
            print(f"✅ {path} ({path.stat().st_size // 1024} KB)")
    else:
        print("Uso: python3 image_gen.py [N|all]")
