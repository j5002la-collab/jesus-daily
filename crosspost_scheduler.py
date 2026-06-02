#!/usr/bin/env python3
"""
CROSSPOST SCHEDULER — Descarga random shorts de @JesusDailyShorts1 y los sube a Facebook.
Selecciona uno aleatorio entre los NO publicados.
Usa cookies de YouTube para evitar bloqueo anti-bot.

Uso:
  python3 crosspost_scheduler.py              → Publicar 1 short aleatorio
  python3 crosspost_scheduler.py --list        → Listar disponibles
  python3 crosspost_scheduler.py --status      → Ver historial
  python3 crosspost_scheduler.py --cookies FILE → Usar archivo cookies específico
"""

import subprocess, json, os, sys, random, urllib.request, urllib.error, urllib.parse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "crosspost_data"
DOWNLOADS = DATA_DIR / "downloads"
STATE_FILE = DATA_DIR / "crosspost_state.json"
LOG_FILE = BASE_DIR / "crosspost.log"
COOKIES_FILE = Path(os.path.expanduser("~")) / "youtube_cookies.txt"

YT_DLP = "/opt/data/yt-dlp"
CHANNEL_URL = "https://www.youtube.com/@JesusDailyShorts1/shorts"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOWNLOADS, exist_ok=True)


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
    return {"posted_ids": [], "history": [], "last_run": None}


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


def get_all_shorts(max_shorts=20):
    """Obtiene todos los shorts disponibles del canal."""
    if not COOKIES_FILE.exists():
        log(f"❌ Cookies no encontradas: {COOKIES_FILE}")
        log("   Exporta cookies: yt-dlp --cookies-from-browser chrome")
        return []

    cmd = [YT_DLP, "--flat-playlist", "--dump-json", CHANNEL_URL,
           "--playlist-end", str(max_shorts),
           "--cookies", str(COOKIES_FILE)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            log(f"❌ yt-dlp error: {result.stderr[:200]}")
            return []

        shorts = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                d = json.loads(line)
                shorts.append({
                    "id": d.get("id"),
                    "title": d.get("title", "Sin título"),
                    "url": f"https://www.youtube.com/shorts/{d.get('id')}",
                    "view_count": d.get("view_count", 0),
                    "duration": d.get("duration", 0),
                })
        return shorts
    except Exception as e:
        log(f"❌ Error: {e}")
        return []


def download_short(video_id):
    """Descarga un short en MP4 usando cookies."""
    url = f"https://www.youtube.com/shorts/{video_id}"
    output = str(DOWNLOADS / f"{video_id}.%(ext)s")
    
    cmd = [YT_DLP, "-f", "best[height<=1080]", "-o", output, url]
    if COOKIES_FILE.exists():
        cmd.extend(["--cookies", str(COOKIES_FILE)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            log(f"❌ Download error: {result.stderr[:200]}")
            return None
        
        # Find downloaded file
        for f in DOWNLOADS.iterdir():
            if video_id in f.name and f.suffix in ['.mp4', '.webm', '.mkv']:
                return str(f)
        return None
    except Exception as e:
        log(f"❌ Error: {e}")
        return None


def upload_video_to_facebook(video_path, caption, page_id, token):
    """Sube video a Facebook usando el endpoint /videos."""
    with open(video_path, 'rb') as f:
        video_data = f.read()

    boundary = '----Boundary7MA4YWxkTrZu0gW'
    body = b''

    # Description
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="description"\r\n\r\n'
    body += caption.encode('utf-8') + b'\r\n'

    # Video file
    fname = os.path.basename(video_path)
    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="source"; filename="{fname}"\r\n'.encode()
    body += b'Content-Type: video/mp4\r\n\r\n'
    body += video_data + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    url = f"https://graph.facebook.com/v20.0/{page_id}/videos?access_token={token}"
    req = urllib.request.Request(url, data=body, headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
    })

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
            if 'id' in result:
                log(f"✅ Video subido! FB ID: {result['id']}")
                return result
            else:
                log(f"⚠️ Respuesta inesperada: {result}")
                return None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        log(f"❌ HTTP {e.code}: {error_body[:300]}")
        return None
    except Exception as e:
        log(f"❌ Error: {e}")
        return None


def cmd_list():
    """Lista shorts disponibles y su estado."""
    state = load_state()
    shorts = get_all_shorts(30)
    
    if not shorts:
        print("\n❌ No se pudieron obtener shorts. ¿Cookies configuradas?")
        return

    print(f"\n📹 Shorts de @JesusDailyShorts1 ({len(shorts)} disponibles)\n")
    print(f"{'Estado':<8} {'Views':<8} {'Título'}")
    print("-" * 70)
    
    available = 0
    for s in shorts:
        posted = s["id"] in state["posted_ids"]
        status = "✅" if posted else "🆕"
        if not posted:
            available += 1
        title = s["title"][:50]
        print(f"{status:<8} {s['view_count']:<8} {title}")
    
    print(f"\n📊 {available} sin publicar | {len(state['posted_ids'])} ya publicados")
    if not COOKIES_FILE.exists():
        print(f"⚠️  Cookies no encontradas en {COOKIES_FILE}")


def cmd_crosspost(cookies_file=None):
    """Selecciona y publica un short aleatorio."""
    global COOKIES_FILE
    if cookies_file:
        COOKIES_FILE = Path(cookies_file)

    env = load_env()
    page_id = env.get("FB_PAGE_ID", "")
    token = env.get("FB_ACCESS_TOKEN", "")

    if not page_id or not token:
        log("❌ Falta FB_PAGE_ID o FB_ACCESS_TOKEN en .env")
        return False

    state = load_state()
    
    # Get all shorts and filter unpublished
    shorts = get_all_shorts(30)
    if not shorts:
        return False

    available = [s for s in shorts if s["id"] not in state["posted_ids"]]
    
    if not available:
        log("🔄 Todos los shorts ya fueron publicados. Reiniciando tracking...")
        state["posted_ids"] = []
        available = shorts

    # Pick random
    short = random.choice(available)
    log(f"🎲 Seleccionado: {short['title']} ({short['view_count']} views)")

    # Download
    video_path = download_short(short["id"])
    if not video_path:
        log("❌ No se pudo descargar el video")
        return False

    # Prepare caption in Spanish with hashtags
    caption = (
        f"{short['title']}\n\n"
        f"📖 Palabra de Dios para ti hoy.\n"
        f"🔥 Síguenos para más contenido cristiano.\n\n"
        f"#JesusDaily #ShortsCristianos #Fe #Biblia #DiosEsAmor "
        f"#CristoVive #Oracion #VidaCristiana"
    )

    # Upload
    result = upload_video_to_facebook(video_path, caption, page_id, token)
    
    if result and 'id' in result:
        log(f"✅ Crosspost exitoso! Short: {short['title']}")
        state["posted_ids"].append(short["id"])
        state["posted_ids"] = state["posted_ids"][-100:]
        state["history"].append({
            "video_id": short["id"],
            "title": short["title"],
            "fb_post_id": result['id'],
            "date": datetime.now().isoformat(),
            "views_on_yt": short["view_count"]
        })
        state["last_run"] = datetime.now().isoformat()
        save_state(state)

        # Clean old downloads
        for f in DOWNLOADS.iterdir():
            if f.stat().st_mtime < datetime.now().timestamp() - 86400:
                f.unlink()
        
        return True
    else:
        log("❌ Falló la publicación")
        return False


def cmd_status():
    state = load_state()
    print(f"\n📊 ESTADO CROSSPOST\n")
    print(f"   Shorts publicados: {len(state['posted_ids'])}")
    print(f"   Último crosspost: {state.get('last_run', 'Nunca')}")
    print(f"   Cookies: {'✅' if COOKIES_FILE.exists() else '❌'} {COOKIES_FILE}")
    
    if state.get("history"):
        print(f"\n📋 Últimos crossposts:")
        for h in state["history"][-5:]:
            print(f"   {h['date'][:10]} | {h['title'][:45]} | FB: {h['fb_post_id']}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        cmd_crosspost()
    elif sys.argv[1] == "--list":
        cmd_list()
    elif sys.argv[1] == "--status":
        cmd_status()
    elif sys.argv[1] == "--cookies" and len(sys.argv) > 2:
        cmd_crosspost(cookies_file=sys.argv[2])
    else:
        print("Uso: python3 crosspost_scheduler.py [--list|--status|--cookies FILE]")
