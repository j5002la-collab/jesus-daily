#!/usr/bin/env python3
"""
INSTAGRAM CROSSPOST — Jesus Daily
Publica imágenes y Reels en Instagram desde Facebook y YouTube.

Uso:
  python3 ig_publisher.py              → Crosspost última imagen de FB a IG
  python3 ig_publisher.py --reel N     → Crosspost short #N de YT a IG Reel
  python3 ig_publisher.py --status     → Ver estado
"""

import json, os, sys, subprocess, random, urllib.request, urllib.error, urllib.parse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "ig_state.json"
IG_ID_FILE = BASE_DIR / "ig_id.txt"
YT_DLP = "/opt/data/yt-dlp"
COOKIES = "/opt/data/youtube_cookies.txt"
CHANNEL = "https://www.youtube.com/@JesusDailyShorts1/shorts"

HOOKS = []  # Sin hooks virales — formato limpio estilo Mensanity
CTAs = []    # Sin CTAs

def load_env():
    env = {}
    for p in [BASE_DIR / ".env"]:
        if p.exists():
            for line in open(p).read().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k] = v
    return env

def load_state():
    if STATE_FILE.exists():
        return json.load(open(STATE_FILE))
    return {"posted_fb_ids": [], "posted_yt_ids": [], "last_run": None}

def save_state(st):
    json.dump(st, open(STATE_FILE, 'w'), indent=2)

def ig_publish_image(image_url, caption, ig_id, token):
    """Publica una imagen en Instagram via URL."""
    cap = urllib.parse.quote(caption)
    url = f"https://graph.facebook.com/v19.0/{ig_id}/media?image_url={urllib.parse.quote(image_url)}&caption={cap}&access_token={token}"
    req = urllib.request.Request(url, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            if result.get('id'):
                cid = result['id']
                url2 = f"https://graph.facebook.com/v19.0/{ig_id}/media_publish?creation_id={cid}&access_token={token}"
                with urllib.request.urlopen(urllib.request.Request(url2, method='POST'), timeout=30) as r2:
                    return json.loads(r2.read())
            return result
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read()).get('error', {}).get('message', str(e))}
    except Exception as e:
        return {"error": str(e)}

def ig_publish_video(video_url, caption, ig_id, token):
    """Publica un Reel en Instagram (video URL público)."""
    cap = urllib.parse.quote(caption)
    url = f"https://graph.facebook.com/v19.0/{ig_id}/media?media_type=REELS&video_url={urllib.parse.quote(video_url)}&caption={cap}&access_token={token}"
    req = urllib.request.Request(url, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            if result.get('id'):
                cid = result['id']
                url2 = f"https://graph.facebook.com/v19.0/{ig_id}/media_publish?creation_id={cid}&access_token={token}"
                with urllib.request.urlopen(urllib.request.Request(url2, method='POST'), timeout=60) as r2:
                    return json.loads(r2.read())
            return result
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read()).get('error', {}).get('message', str(e))}
    except Exception as e:
        return {"error": str(e)}

def get_latest_fb_image(page_id, token):
    """Obtiene URL de la última imagen publicada en Facebook."""
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed?fields=id,message,full_picture&limit=5&access_token={token}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            for post in data.get('data', []):
                pic = post.get('full_picture', '')
                msg = (post.get('message') or '')[:100]
                if pic and post['id']:
                    return post['id'], pic, msg
    except Exception as e:
        print(f"Error FB: {e}")
    return None, None, None

def cmd_crosspost_fb():
    """Crosspostea la última imagen de FB a Instagram."""
    env = load_env()
    page_id = env.get('FB_PAGE_ID', '')
    token = env.get('FB_ACCESS_TOKEN', '')
    
    if not IG_ID_FILE.exists():
        print("❌ Instagram no configurado. Corre primero la detección de IG.")
        return False
    
    ig_id = open(IG_ID_FILE).read().strip()
    state = load_state()
    
    # Get latest FB image
    fb_id, img_url, fb_msg = get_latest_fb_image(page_id, token)
    if not img_url:
        print("❌ No se encontró imagen en Facebook")
        return False
    
    if fb_id in state.get('posted_fb_ids', []):
        print("✅ Última imagen ya crossposteada a IG")
        return True
    
    # Build caption — formato limpio estilo Mensanity
    # FB caption ya tiene el formato correcto, lo usamos tal cual
    caption = fb_msg if fb_msg else "Palabra de Dios para ti hoy.\n\n#JesusDaily #CristoEsRey ✝️"
    # Aseguramos hashtags de marca
    if "#GlobalJesus" not in caption:
        caption += "\n#GlobalJesus #CristoEsRey ✝️"
    
    print(f"📸 Crossposteando FB → IG: {fb_msg[:60]}...")
    result = ig_publish_image(img_url, caption, ig_id, token)
    
    if 'id' in result:
        print(f"✅ IG: {result['id']}")
        state['posted_fb_ids'] = (state.get('posted_fb_ids', []) + [fb_id])[-50:]
        state['last_run'] = datetime.now().isoformat()
        save_state(state)
        return True
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")
        return False

def cmd_status():
    state = load_state()
    print(f"\n📊 INSTAGRAM CROSSPOST STATUS\n")
    print(f"   FB posts crossposteados: {len(state.get('posted_fb_ids', []))}")
    print(f"   YT shorts crossposteados: {len(state.get('posted_yt_ids', []))}")
    print(f"   Último: {state.get('last_run', 'Nunca')}")
    if IG_ID_FILE.exists():
        print(f"   IG ID: {open(IG_ID_FILE).read().strip()}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        cmd_crosspost_fb()
    elif sys.argv[1] == "--status":
        cmd_status()
    else:
        print("Uso: python3 ig_publisher.py [--status]")
