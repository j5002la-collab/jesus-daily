#!/usr/bin/env python3
"""
Generador de imágenes PNG puras para Jesus Daily.
Sin dependencias externas — bitmap fonts built-in.
Estilo: fondo oscuro con texto blanco, atmosférico.
"""

import struct
import zlib
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# 5x7 bitmap font for basic ASCII
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
    'Q': [0b01110, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101, 0b00000],
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
    ';': [0b00000, 0b00100, 0b00000, 0b00000, 0b00100, 0b01000, 0b00000],
    '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100, 0b00000],
    '?': [0b01110, 0b10001, 0b00010, 0b00100, 0b00000, 0b00100, 0b00000],
    '-': [0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000],
    "'": [0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '"': [0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '(': [0b00010, 0b00100, 0b00100, 0b00100, 0b00100, 0b00010, 0b00000],
    ')': [0b01000, 0b00100, 0b00100, 0b00100, 0b00100, 0b01000, 0b00000],
    '/': [0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000, 0b00000],
    '\\': [0b10000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00000, 0b00000],
    '&': [0b01100, 0b10010, 0b01100, 0b10110, 0b10001, 0b01110, 0b00000],
    '*': [0b00000, 0b10101, 0b01110, 0b10101, 0b00000, 0b00000, 0b00000],
    '+': [0b00000, 0b00100, 0b01110, 0b00100, 0b00000, 0b00000, 0b00000],
    '=': [0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
    '@': [0b01110, 0b10001, 0b10111, 0b10101, 0b10000, 0b01110, 0b00000],
    '#': [0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b00000, 0b00000],
    '$': [0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
    '%': [0b11001, 0b11010, 0b00100, 0b01011, 0b10011, 0b00000, 0b00000],
    '^': [0b00100, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '_': [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000],
    '`': [0b01000, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '|': [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    '~': [0b00000, 0b00000, 0b01101, 0b10110, 0b00000, 0b00000, 0b00000],
    '<': [0b00010, 0b00100, 0b01000, 0b00100, 0b00010, 0b00000, 0b00000],
    '>': [0b01000, 0b00100, 0b00010, 0b00100, 0b01000, 0b00000, 0b00000],
    '[': [0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110, 0b00000],
    ']': [0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110, 0b00000],
    '{': [0b00010, 0b00100, 0b01100, 0b00100, 0b00010, 0b00000, 0b00000],
    '}': [0b01000, 0b00100, 0b00110, 0b00100, 0b01000, 0b00000, 0b00000],
    # Spanish characters (approximations with bitmap)
    'á': [0b00010, 0b00100, 0b01110, 0b10001, 0b11111, 0b10001, 0b10001],
    'é': [0b00010, 0b00100, 0b11111, 0b10000, 0b11110, 0b10000, 0b11111],
    'í': [0b00010, 0b00100, 0b01110, 0b00100, 0b00100, 0b00100, 0b01110],
    'ó': [0b00010, 0b00100, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110],
    'ú': [0b00010, 0b00100, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'ñ': [0b00000, 0b01101, 0b10110, 0b10001, 0b10001, 0b10001, 0b10001],
    'Ñ': [0b01101, 0b10110, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001],
    '¡': [0b00100, 0b00000, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    '¿': [0b01110, 0b10001, 0b00010, 0b00100, 0b00000, 0b00100, 0b00000],
}

# Lowercase map to uppercase
for c in 'abcdefghijklmnopqrstuvwxyz':
    BITMAP_FONT[c] = BITMAP_FONT[c.upper()]


def draw_char(pixels, char, x, y, scale, color, W, H):
    """Draw a bitmap character at position (x,y) with given scale."""
    if char not in BITMAP_FONT:
        return
    bitmap = BITMAP_FONT[char]
    for row in range(7):
        for col in range(5):
            if bitmap[row] & (1 << (4 - col)):
                for dy in range(scale):
                    for dx in range(scale):
                        px = x + col * scale + dx
                        py = y + row * scale + dy
                        if 0 <= px < W and 0 <= py < H:
                            offset = 1 + (py * W + px) * 4
                            pixels[offset:offset+3] = color


def draw_text(pixels, text, x, y, scale, color, W, H):
    """Draw a string of text starting at (x,y)."""
    cx = x
    for char in text:
        if char == '\n':
            return  # Handle line breaks manually
        draw_char(pixels, char, cx, y, scale, color, W, H)
        cx += 6 * scale


def text_width(text, scale):
    return len(text) * 6 * scale


def generate_image(day, post_data):
    """Generate a cinematic PNG for a Jesus Daily post."""
    W, H = 1080, 1080
    H_FULL = 1350  # 4:5 for better FB display

    # Dark atmospheric background
    raw = bytearray()
    for y in range(H_FULL):
        raw.append(0)  # filter byte
        for x in range(W):
            # Gradient: darker at bottom
            t = y / H_FULL
            r = int(10 + t * 20)
            g = int(8 + t * 15)
            b = int(18 + t * 25)
            a = 255
            raw.extend(struct.pack('BBBB', r, g, b, a))

    # Draw cross in background (subtle)
    cx, cy = W // 2, H_FULL // 3
    cross_color = struct.pack('BBB', 40, 35, 45)
    for dx in range(-2, 3):
        for dy in range(-80, 81):
            px, py = cx + dx, cy + dy
            if 0 <= px < W and 0 <= py < H_FULL:
                offset = 1 + (py * W + px) * 4
                raw[offset:offset+3] = cross_color
    for dy in range(-2, 3):
        for dx in range(-40, 41):
            px, py = cx + dx, cy + dy
            if 0 <= px < W and 0 <= py < H_FULL:
                offset = 1 + (py * W + px) * 4
                raw[offset:offset+3] = cross_color

    # Category emoji and label at top
    emoji = post_data.get("emoji", "✝️")
    category = post_data.get("category", "fe").upper()
    
    # Draw category bar
    for y in range(40, 90):
        for x in range(80, W - 80):
            if 45 <= y <= 85:
                offset = 1 + (y * W + x) * 4
                raw[offset:offset+3] = b'\x50\x40\x30'  # gold/amber

    # Main title
    title_scale = 4
    title = "JESUS DAILY"
    tw = text_width(title, title_scale)
    draw_text(raw, title, (W - tw) // 2, 110, title_scale, b'\xff\xd7\x00', W, H_FULL)

    # Day counter
    day_text = f"DIA {post_data.get('day', 1)}"
    day_scale = 2
    dw = text_width(day_text, day_scale)
    draw_text(raw, day_text, (W - dw) // 2, 170, day_scale, b'\xff\xd7\x00', W, H_FULL)

    # Verse (main content)
    verse = post_data.get("verse", "")
    verse_scale = 3
    font_h = 7 * verse_scale
    line_w = 80 * verse_scale  # Max chars per line
    
    # Word wrap
    words = verse.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if text_width(test_line, verse_scale) < W - 160:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Truncate to 10 lines
    lines = lines[:10]

    # Draw verse lines centered
    start_y = 230
    verse_color = b'\xff\xff\xff'
    for i, line in enumerate(lines):
        lw = text_width(line, verse_scale)
        draw_text(raw, line, (W - lw) // 2, start_y + i * (font_h + 15), 
                 verse_scale, verse_color, W, H_FULL)

    ref = f"— {post_data.get('reference', '')}"
    ref_scale = 2
    rw = text_width(ref, ref_scale)
    ref_y = start_y + len(lines) * (font_h + 15) + 20
    draw_text(raw, ref, (W - rw) // 2, ref_y, ref_scale, b'\xc0\xa0\x60', W, H_FULL)

    # Reflection at bottom
    reflection = post_data.get("reflection", "")
    refl_scale = 2
    ref_words = reflection.split()
    ref_lines = []
    current = ""
    for word in ref_words:
        test = current + (" " if current else "") + word
        if text_width(test, refl_scale) < W - 200:
            current = test
        else:
            if current:
                ref_lines.append(current)
            current = word
    if current:
        ref_lines.append(current)

    ref_lines = ref_lines[:5]

    ref_start_y = H_FULL - 280
    refl_color = b'\xd0\xd0\xd0'
    for i, line in enumerate(ref_lines):
        lw = text_width(line, refl_scale)
        draw_text(raw, line, (W - lw) // 2, ref_start_y + i * (7 * refl_scale + 10),
                 refl_scale, refl_color, W, H_FULL)

    # Bottom branding
    brand_scale = 2
    brand = "#JesusDaily"
    bw = text_width(brand, brand_scale)
    draw_text(raw, brand, (W - bw) // 2, H_FULL - 60, brand_scale, b'\xff\xd7\x00', W, H_FULL)

    # PNG encoding
    def chunk(ctype, data):
        c = ctype + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H_FULL, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw))
    png_data = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

    output_path = IMAGES_DIR / f"dia_{day:03d}.png"
    with open(output_path, 'wb') as f:
        f.write(png_data)
    
    return output_path


def generate_all():
    """Genera imágenes para todos los posts."""
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
    
    print("✅ Generación completa")


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            generate_all()
        else:
            day = int(sys.argv[1])
            posts_file = BASE_DIR / "posts.json"
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
            if day <= len(posts):
                post = posts[day - 1]
                path = generate_image(day, post)
                print(f"✅ Imagen generada: {path}")
            else:
                print(f"❌ Día {day} fuera de rango (max {len(posts)})")
    else:
        print("Uso: python3 image_gen.py [N|all]")
