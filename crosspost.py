#!/usr/bin/env python3
"""
Crosspost YouTube Shorts → Facebook Reels.
Descarga el último short de @JesusDailyShorts1 y lo sube a Facebook como Reel.

Uso:
  python3 crosspost.py           → Subir el short más reciente
  python3 crosspost.py --dry-run → Solo descargar, no publicar
  python3 crosspost.py --list    → Listar últimos shorts sin descargar
  python3 crosspost.py --id VIDEO_ID → Crosspostear un short específico
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "crosspost_data"
STATE_FILE = DATA_DIR / "crosspost_state.json"
DOWNLOAD_DIR = DATA_DIR / "downloads"
LOG_FILE = BASE_DIR / "crosspost.log"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

CHANNEL_URL = "https://www.youtube.com/@JesusDailyShorts1/shorts"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"posted_ids": [], "last_check": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_env():
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


YT_DLP = "/opt/data/yt-dlp"
COOKIES_FILE = "/opt/data/youtube_cookies.txt"

def get_latest_shorts(limit=5):
    """Obtiene los últimos shorts del canal usando yt-dlp."""
    try:
        result = subprocess.run(
            [YT_DLP, "--flat-playlist", "--dump-json", 
             CHANNEL_URL, "--playlist-end", str(limit),
             "--cookies", COOKIES_FILE],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            log(f"yt-dlp error: {result.stderr[:200]}")
            return []

        shorts = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                d = json.loads(line)
                shorts.append({
                    "id": d.get("id"),
                    "title": d.get("title", "Sin título"),
                    "url": f"https://www.youtube.com/shorts/{d.get('id')}",
                    "duration": d.get("duration", 0),
                    "view_count": d.get("view_count", 0),
                })
        return shorts
    except subprocess.TimeoutExpired:
        log("Timeout obteniendo shorts")
        return []
    except FileNotFoundError:
        log("yt-dlp no instalado. pip install yt-dlp")
        return []
    except Exception as e:
        log(f"Error: {e}")
        return []


def download_short(video_id):
    """Descarga un short en formato MP4."""
    url = f"https://www.youtube.com/shorts/{video_id}"
    output_template = str(DOWNLOAD_DIR / f"{video_id}.%(ext)s")

    try:
        result = subprocess.run(
            [YT_DLP, "-f", "best[height<=1080]", "-o", output_template, url,
            "--cookies", COOKIES_FILE],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            log(f"Error descargando: {result.stderr[:200]}")
            return None

        # Find the downloaded file
        for f in DOWNLOAD_DIR.iterdir():
            if video_id in f.name:
                return str(f)
        return None
    except Exception as e:
        log(f"Error: {e}")
        return None


def upload_reel_to_facebook(video_path, caption, page_id, token):
    """Sube un video como Reel a Facebook usando la Graph API."""
    if not page_id or not token:
        log("❌ Sin credenciales de Facebook")
        return None

    with open(video_path, 'rb') as f:
        video_data = f.read()

    boundary = '----Boundary7MA4YWxkTrZu0gW'
    body = b''

    # Caption
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="description"\r\n\r\n'
    body += caption.encode('utf-8') + b'\r\n'

    # Video
    fname = os.path.basename(video_path)
    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="source"; filename="{fname}"\r\n'.encode()
    body += b'Content-Type: video/mp4\r\n\r\n'
    body += video_data + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    # Facebook Reels endpoint (v20.0+)
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    
    try:
        # First, upload video
        upload_url = f"https://graph.facebook.com/v20.0/{page_id}/videos"
        req = urllib.request.Request(
            f"{upload_url}?access_token={token}",
            data=body,
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        
        if 'id' in result:
            log(f"✅ Video subido: {result['id']}")
            return result
        else:
            log(f"❌ Error: {result}")
            return None
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        log(f"❌ HTTP {e.code}: {error_body[:300]}")
        return {"error": error_body}
    except Exception as e:
        log(f"❌ Error: {e}")
        return {"error": str(e)}


def cmd_crosspost(video_id=None, dry_run=False):
    """Crosspostea un short a Facebook."""
    env = load_env()
    page_id = env.get("FB_PAGE_ID", "")
    token = env.get("FB_ACCESS_TOKEN", "")

    if not page_id or not token:
        log("❌ Configura FB_PAGE_ID y FB_ACCESS_TOKEN en .env")
        return False

    state = load_state()

    if video_id:
        shorts = [{"id": video_id, "title": "Short específico", "url": f"https://youtube.com/shorts/{video_id}"}]
    else:
        shorts = get_latest_shorts(5)
        if not shorts:
            log("❌ No se pudieron obtener shorts")
            return False

        # Filtrar ya publicados
        shorts = [s for s in shorts if s["id"] not in state["posted_ids"]]
        if not shorts:
            log("✅ Todos los shorts ya fueron crossposteados")
            return True

    short = shorts[0]
    log(f"📹 Crossposteando: {short['title']} ({short['id']})")

    # Descargar
    video_path = download_short(short["id"])
    if not video_path:
        log("❌ No se pudo descargar el video")
        return False

    log(f"📥 Descargado: {video_path}")

    if dry_run:
        log(f"🔍 DRY RUN - No se publica. Video en: {video_path}")
        return True

    # Preparar caption
    caption = (
        f"{short['title']}\n\n"
        f"📖 Palabra de Dios para ti hoy.\n"
        f"🎥 @JesusDailyShorts1\n\n"
        f"#JesusDaily #ShortsCristianos #Fe #Biblia #ReelsCristianos"
    )

    # Subir a Facebook
    result = upload_reel_to_facebook(video_path, caption, page_id, token)
    
    if result and 'id' in result:
        log(f"✅ Crosspost exitoso! Facebook ID: {result['id']}")
        state["posted_ids"].append(short["id"])
        state["last_check"] = datetime.now().isoformat()
        # Keep only last 100 IDs
        state["posted_ids"] = state["posted_ids"][-100:]
        save_state(state)

        # Limpiar video descargado después de 24h
        return True
    else:
        log("❌ Falló la publicación en Facebook")
        return False


def cmd_list():
    """Lista últimos shorts del canal."""
    shorts = get_latest_shorts(10)
    state = load_state()
    
    print(f"\n📹 Últimos shorts de @JesusDailyShorts1\n")
    print(f"{'Publicado':<10} {'ID':<15} {'Título':<50} {'Views':<10}")
    print("-" * 85)
    for s in shorts:
        status = "✅" if s["id"] in state["posted_ids"] else "⏳"
        print(f"{status:<10} {s['id']:<15} {s['title'][:48]:<50} {s.get('view_count', '?'):<10}")
    
    print(f"\nTotal crossposteados: {len(state['posted_ids'])}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        cmd_crosspost()
    elif sys.argv[1] == "--list":
        cmd_list()
    elif sys.argv[1] == "--dry-run":
        cmd_crosspost(dry_run=True)
    elif sys.argv[1] == "--id" and len(sys.argv) > 2:
        cmd_crosspost(video_id=sys.argv[2])
    else:
        print("Uso: python3 crosspost.py [--list|--dry-run|--id VIDEO_ID]")
