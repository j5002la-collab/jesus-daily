#!/usr/bin/env python3
"""
Facebook Publisher para Jesus Daily.
Publica imágenes + caption en Facebook con estilo cristiano/oscuro.
"""
import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"


def load_env():
    """Carga variables desde .env"""
    env = {}
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k] = v
    return env


def format_caption(post):
    """Caption viral optimizado — hook + cta + hashtags trending."""
    # Inline viral optimization (avoids import issues with Hermes)
    HOOKS = [
        "🔥 Esto cambió mi vida hoy...",
        "😭 Leí esto y no pude contener las lágrimas...",
        "💔 Si estás pasando por algo difícil, esto es para ti...",
        "🙏 Dios me habló con este versículo hoy...",
        "⚠️ El 99% de cristianos ignora este versículo...",
        "🤔 ¿Crees que esto es casualidad?",
        "📖 El versículo más poderoso que casi nadie lee...",
        "🕊️ Esto es lo que Dios quiere decirte HOY...",
        "🔥 Esta palabra es para ti. Sí, para TI.",
        "⏰ 30 segundos que pueden cambiar tu día...",
    ]
    CTAs = [
        "❤️ Dale LIKE si Dios te habló hoy",
        "💬 Comenta tu versículo favorito abajo",
        "↗️ COMPARTE esta palabra — podrías cambiar el día de alguien",
        "🙏 Escribe AMÉN si crees en los milagros",
        "👇 Etiqueta a un amigo que necesite escuchar esto",
        "🔥 Síguenos para recibir la palabra de Dios cada día",
        "📲 Guarda este post para volver a leerlo cuando lo necesites",
    ]
    import random, datetime
    hook = random.choice(HOOKS)
    cta = random.choice(CTAs)
    day = datetime.datetime.now().weekday()
    month = datetime.datetime.now().month
    
    # Trending hashtags rotativos
    broad = random.choice([
        "#Viral #FYP #Parati #Trending #ReelsFacebook",
        "#Viral #Reels #ParaTi #Tendencia #DiosEsAmor",
        "#FYPシ #Viral2026 #Dios #CristoVive #Trending",
    ])
    niche = random.choice([
        "#JesusDaily #FeCristiana #Biblia #Oracion",
        "#PalabraDeDios #Devocional #CristoRey #Fe",
        "#Fe #Esperanza #AmorDeDios #OracionDiaria",
    ])
    hashtags = f"{broad} {niche}"
    
    return (
        f"{hook}\n\n"
        f"\"{post['verse']}\"\n"
        f"— {post['reference']}\n\n"
        f"{post['reflection']}\n\n"
        f"{cta}\n\n"
        f"{hashtags}\n"
        f"#JesusDaily #CristoEsRey ✝️"
    )


def generate_image(post, output_path):
    """Genera imagen PNG pura para el post. 
    Usa image_gen.py si existe, sino genera una simple con texto."""
    gen_script = BASE_DIR / "image_gen.py"
    if gen_script.exists():
        result = subprocess.run(
            ["python3", str(gen_script), str(post["day"])],
            capture_output=True, text=True, timeout=30,
            cwd=str(BASE_DIR)
        )
        return Path(output_path).exists()
    
    # Fallback: generate simple PNG
    try:
        create_simple_png(post, output_path)
        return True
    except Exception:
        return False


def create_simple_png(post, output_path):
    """Genera un PNG simple con texto usando bitmap fonts (sin Pillow)."""
    text = post["verse"]
    ref = f"— {post['reference']}"
    
    # Simple 5x7 bitmap font (numbers + basic chars)
    # This is a minimal font for fallback
    import struct
    import zlib

    W, H = 1080, 1080
    # Create black background
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter byte
        raw.extend(b'\x00\x00\x00\x00' * W)  # RGBA black

    # Add minimal text - white cross/center
    cx, cy = W // 2, H // 2
    cross_size = 80
    for dy in range(-cross_size, cross_size + 1):
        y = cy + dy
        if 0 <= y < H:
            offset = 1 + (y * W + cx) * 4
            raw[offset:offset+3] = b'\xff\xff\xff'
    for dx in range(-cross_size, cross_size + 1):
        x = cx + dx
        if 0 <= x < W:
            offset = 1 + (cy * W + x) * 4
            raw[offset:offset+3] = b'\xff\xff\xff'

    # PNG encode
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw))
    
    png_data = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')
    
    with open(output_path, 'wb') as f:
        f.write(png_data)


def publish_photo(page_id, token, image_path, caption):
    """Sube una foto a Facebook con caption usando multipart."""
    with open(image_path, 'rb') as f:
        image_data = f.read()

    boundary = '----Boundary7MA4YWxkTrZu0gW'
    body = b''

    # Caption
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="message"\r\n\r\n'
    body += caption.encode('utf-8') + b'\r\n'

    # Image
    fname = os.path.basename(image_path)
    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="source"; filename="{fname}"\r\n'.encode()
    body += b'Content-Type: image/png\r\n\r\n'
    body += image_data + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    url = f"https://graph.facebook.com/v19.0/{page_id}/photos?access_token={token}"
    req = urllib.request.Request(url, data=body, headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
    })

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read()).get('error', {}).get('message', str(e))}
    except Exception as e:
        return {"error": str(e)}


def publish_post(day=None):
    """Publica el post del día (o un día específico)."""
    env = load_env()
    page_id = env.get("FB_PAGE_ID", "")
    token = env.get("FB_ACCESS_TOKEN", "")

    if not token or len(token) < 20:
        print("❌ No hay token de Facebook configurado en .env")
        return False

    # Determine ciclo y cargar posts
    state_path = BASE_DIR / "state.json"
    if state_path.exists():
        with open(state_path) as f:
            state = json.load(f)
    else:
        state = {"current_day": 0, "total_published": 0, "last_published": None, "cycles_completed": 0}

    current = state.get("current_day", 0)
    cycle = state.get("cycles_completed", 0)

    # Cargar ciclo correcto
    if cycle == 0:
        posts_file = BASE_DIR / "posts.json"
    else:
        posts_file = BASE_DIR / f"posts_ciclo{cycle + 1}.json"
        if not posts_file.exists():
            print(f"⚠️  {posts_file.name} no existe, usando posts.json")
            posts_file = BASE_DIR / "posts.json"
            cycle = 0

    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    # Determinar qué post publicar
    if day is None:
        if current >= len(posts):
            current = 0
            cycle += 1
            state["cycles_completed"] = cycle
            next_file = BASE_DIR / f"posts_ciclo{cycle + 1}.json"
            if next_file.exists():
                with open(next_file, "r", encoding="utf-8") as f:
                    posts = json.load(f)
            else:
                cycle = 0
                state["cycles_completed"] = 0
                with open(BASE_DIR / "posts.json", "r", encoding="utf-8") as f:
                    posts = json.load(f)
        post = posts[current]
    else:
        post = posts[day - 1]  # day 1-indexed

    # Intentar generar imagen
    image_file = IMAGES_DIR / f"dia_{post['day']:03d}.png"
    if not image_file.exists():
        generate_image(post, str(image_file))

    # Formatear caption
    caption = format_caption(post)

    print(f"📤 Publicando Día {post['day']} (Ciclo {cycle + 1})...")
    print(f"   Categoría: {post['category']}")
    print(f"   Referencia: {post['reference']}")
    print(f"   Imagen: {image_file.name} {'✅' if image_file.exists() else '❌'}")

    # Publicar con imagen si existe
    result = None
    if image_file.exists() and image_file.stat().st_size > 0:
        result = publish_photo(page_id, token, str(image_file), caption)
        if 'id' not in result:
            print(f"   ⚠️ Imagen falló, intentando texto...")
    
    if not result or 'id' not in result:
        # Text-only fallback
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        data = f"message={urllib.parse.quote(caption)}&access_token={token}".encode()
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
        except Exception as e:
            result = {"error": str(e)}

    if 'id' in result:
        print(f"✅ PUBLICADO! Post ID: {result['id']}")
        if day is None:
            state["current_day"] += 1
            state["total_published"] = state.get("total_published", 0) + 1
            from datetime import datetime
            state["last_published"] = datetime.now().isoformat()
            with open(BASE_DIR / "state.json", "w") as f:
                json.dump(state, f, indent=2)
            print(f"   Siguiente: Día {state['current_day'] + 1}")
        return True
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        day = int(sys.argv[1])
        publish_post(day=day)
    else:
        publish_post()
