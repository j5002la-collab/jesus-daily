#!/usr/bin/env python3
"""
Generador de imágenes para Jesus Daily.
Atardecer + cruz dorada. SIN texto incrustado (va en el caption de Facebook).
Facebook rechaza imágenes con texto renderizado programáticamente.
"""

import struct, zlib, os, random, json, sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
os.makedirs(IMAGES_DIR, exist_ok=True)


def generate_image(day):
    """Atardecer degradado + cruz dorada central. Limpio, sin texto."""
    W, H = 1080, 1080
    random.seed(day * 137 + 42)

    raw = bytearray()
    for y in range(H):
        raw.append(0)  # PNG filter byte
        t = y / H
        for x in range(W):
            hx = x / W
            
            if t < 0.35:
                # Sky: blue to purple
                r = 50 + int(t * 80 + hx * 30)
                g = 60 + int(t * 90 + hx * 20)
                b = 130 + int(t * 70 + hx * 40)
            elif t < 0.55:
                # Horizon: warm transition
                s = (t - 0.35) / 0.20
                r = 130 + int(s * 100)
                g = 150 - int(s * 20)
                b = 200 - int(s * 120)
            else:
                # Ground: earthy tones
                s = (t - 0.55) / 0.45
                r = 230 - int(s * 120)
                g = 130 - int(s * 70)
                b = 80 + int(s * 30)

            # Noise for photographic texture
            n = random.randint(-8, 8)
            r = max(0, min(255, r + n))
            g = max(0, min(255, g + n))
            b = max(0, min(255, b + n))

            raw.extend(struct.pack('BBBB', r, g, b, 255))

    # Cruz dorada central (gruesa, visible)
    gold = b'\xd4\xaf\x37'
    cx, cy = W // 2, 540

    for dx in range(-7, 8):
        for dy in range(-100, 101):
            px, py = cx + dx, cy + dy
            if 0 <= px < W and 0 <= py < H:
                off = 1 + (py * W + px) * 4
                raw[off:off+3] = gold

    for dy in range(-7, 8):
        for dx in range(-75, 76):
            px, py = cx + dx, cy + dy
            if 0 <= px < W and 0 <= py < H:
                off = 1 + (py * W + px) * 4
                raw[off:off+3] = gold

    # PNG encode
    def chunk(ct, d):
        c = ct + d
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(d)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw))
    png = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

    path = IMAGES_DIR / f"dia_{day:03d}.png"
    with open(path, 'wb') as f:
        f.write(png)
    return path


def generate_all():
    posts_file = BASE_DIR / "posts.json"
    if not posts_file.exists():
        print("❌ posts.json no encontrado")
        return
    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)
    print(f"Generando {len(posts)} imágenes...")
    for post in posts:
        day = post["day"]
        out = IMAGES_DIR / f"dia_{day:03d}.png"
        if out.exists():
            print(f"  ⏭️  Día {day} ya existe")
            continue
        generate_image(day)
        print(f"  ✅ Día {day}")
    print("✅ Completo")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            generate_all()
        else:
            day = int(sys.argv[1])
            path = generate_image(day)
            print(f"✅ {path} ({path.stat().st_size // 1024} KB)")
    else:
        print("Uso: python3 image_gen.py [N|all]")
