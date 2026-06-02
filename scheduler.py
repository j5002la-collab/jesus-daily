#!/usr/bin/env python3
"""
🕊️ JESUS DAILY SCHEDULER
Publica mensajes cristianos/católicos diarios en Facebook.

Modos:
  python3 scheduler.py next     → Muestra el mensaje de hoy
  python3 scheduler.py publish  → Publica en Facebook (imagen + texto)
  python3 scheduler.py status   → Estado y progreso
  python3 scheduler.py reset    → Reiniciar ciclo
  python3 scheduler.py skip N   → Adelantar/retroceder N días
  python3 scheduler.py list     → Listar resumen de posts
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
POSTS_FILE = BASE_DIR / "posts.json"
STATE_FILE = BASE_DIR / "state.json"

CATEGORY_EMOJIS = {
    "fe": "🙏", "esperanza": "🕊️", "amor": "❤️",
    "oracion": "🛐", "gratitud": "✨", "biblia": "📖",
    "jesus": "✝️", "maria": "🌹", "santos": "👼",
    "misericordia": "💛", "paz": "☮️", "fortaleza": "💪",
    "perdon": "🤲", "humildad": "🌿", "perseverancia": "🏔️",
    "sabiduria": "🦉", "alegria": "😇", "confianza": "⚓",
    "servicio": "🤝", "eternidad": "🌟",
}


def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "current_day": 0,
        "total_published": 0,
        "last_published": None,
        "cycles_completed": 0
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def format_message(post):
    """Formatea un mensaje cristiano para Facebook."""
    emoji = post.get("emoji", "✝️")
    cat_name = post.get("category", "fe").capitalize()

    msg = f"""{emoji} {cat_name} | DÍA {post['day']} {emoji}

"{post['verse']}"

— {post['reference']}

{post['reflection']}

💬 ¿Qué te dice Dios hoy a través de esta palabra? Compártelo en los comentarios.

{post['hashtags']}
#JesusDaily #CristoEsRey #VidaCristiana"""
    return msg


def get_today_post(posts, state):
    """Obtiene el post del día actual."""
    day = state["current_day"]
    if day >= len(posts):
        day = 0
        state["current_day"] = 0
        state["cycles_completed"] = state.get("cycles_completed", 0) + 1
        save_state(state)
        print("🔄 Ciclo completado. Reiniciando desde Día 1.")
    return posts[day]


def publish_to_facebook(post):
    """Publica en Facebook via Graph API."""
    page_id = os.environ.get("FB_PAGE_ID")
    access_token = os.environ.get("FB_ACCESS_TOKEN")

    if not page_id or not access_token:
        env_path = BASE_DIR / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("FB_PAGE_ID="):
                        page_id = line.split("=", 1)[1]
                    elif line.startswith("FB_ACCESS_TOKEN="):
                        access_token = line.split("=", 1)[1]

    if not page_id or not access_token or len(access_token) < 20:
        print("❌ Faltan credenciales de Facebook en .env")
        return None

    try:
        import urllib.request
        import urllib.error
        import urllib.parse
    except ImportError:
        print("❌ urllib no disponible")
        return None

    message = format_message(post)
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    data = f"message={urllib.parse.quote(message)}&access_token={access_token}".encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read()).get("error", {}).get("message", str(e))}
    except Exception as e:
        return {"error": str(e)}


def cmd_next():
    posts = load_posts()
    state = load_state()
    post = get_today_post(posts, state)
    print(format_message(post))
    print(f"\n📊 Progreso: Día {post['day']}/500 | Publicados: {state['total_published']}")
    print("Para publicar: python3 scheduler.py publish")


def cmd_publish():
    posts = load_posts()
    state = load_state()

    if state["current_day"] >= len(posts):
        state["current_day"] = 0
        state["cycles_completed"] = state.get("cycles_completed", 0) + 1
        print("🔄 Nuevo ciclo iniciado.")

    post = get_today_post(posts, state)
    print(f"📝 Preparando: Día {post['day']} — {post['category']} ({post['reference']})")

    # Try publishing with image first
    from fb_publisher import publish_post
    success = publish_post()

    if not success:
        # Fallback to text-only
        result = publish_to_facebook(post)
        if result and "id" in result:
            print(f"✅ Publicado (texto)! ID: {result['id']}")
            success = True
            post_id = result['id']
        elif result:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
            print("\n💡 COPIA MANUAL:")
            print("=" * 60)
            print(format_message(post))
            print("=" * 60)
            return

    if success:
        state["current_day"] += 1
        state["total_published"] += 1
        state["last_published"] = datetime.now().isoformat()
        save_state(state)
        print(f"📈 Avanzado a día {state['current_day'] + 1}")


def cmd_status():
    posts = load_posts()
    state = load_state()
    day = state["current_day"]

    print("🕊️ JESUS DAILY — ESTADO")
    print(f"   Mensajes totales: {len(posts)}")
    print(f"   Publicados: {state['total_published']}")
    print(f"   Día actual: {day + 1}/500")
    print(f"   Ciclos completados: {state.get('cycles_completed', 0)}")
    print(f"   Última publicación: {state['last_published'] or 'Nunca'}")

    if day < len(posts):
        post = posts[day]
        print(f"\n📌 Próximo: Día {post['day']} — {post['category']}")
        print(f"   «{post['verse'][:80]}...»")


def cmd_reset():
    confirm = input("¿Reiniciar desde Día 1? (s/n): ")
    if confirm.lower() == "s":
        state = {"current_day": 0, "total_published": 0, 
                 "last_published": None, "cycles_completed": 0}
        save_state(state)
        print("🔄 Reiniciado. Próximo post: Día 1.")


def cmd_skip(days):
    posts = load_posts()
    state = load_state()
    new_day = state["current_day"] + days
    if new_day < 0:
        new_day = 0
    elif new_day >= len(posts):
        new_day = new_day % len(posts)
        state["cycles_completed"] = state.get("cycles_completed", 0) + 1
    state["current_day"] = new_day
    save_state(state)
    print(f"{'⏭️' if days > 0 else '⏪'} Día {new_day + 1}/500")


def cmd_list():
    posts = load_posts()
    state = load_state()
    current = state["current_day"]
    print(f"{'Día':<5} {'Cat':<12} {'Ref':<22} {'Mensaje (inicio)':<55}")
    print("-" * 94)
    for post in posts:
        status = "✅" if post["day"] <= current else "⏳"
        marker = "◀ HOY" if post["day"] == current + 1 else ""
        print(f"{post['day']:<5} {post['category']:<12} {post['reference'][:20]:<22} {post['verse'][:52]:<55} {status} {marker}")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "next"

    if command == "next":
        cmd_next()
    elif command == "publish":
        cmd_publish()
    elif command == "status":
        cmd_status()
    elif command == "reset":
        cmd_reset()
    elif command == "skip":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        cmd_skip(days)
    elif command == "list":
        cmd_list()
    else:
        print("Uso: python3 scheduler.py [next|publish|status|reset|skip N|list]")
        sys.exit(1)
