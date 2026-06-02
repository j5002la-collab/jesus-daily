#!/usr/bin/env python3
"""
VIRAL CONTENT OPTIMIZER — Jesus Daily
Optimiza captions, hashtags y hooks para maximizar engagement y viralidad.

Estrategias:
  1. Hook hooks — primeras 3 líneas que atrapan
  2. Emotional triggers — preguntas que generan comentarios
  3. Share bait — "comparte si", "etiqueta a alguien"
  4. Trending hashtags rotativos
  5. CTA fuerte al final

Uso:
  python3 viral_optimizer.py              → Muestra estrategia actual
  python3 viral_optimizer.py --post 5     → Optimiza el post día 5
  python3 viral_optimizer.py --hashtags   → Muestra hashtags trending
  python3 viral_optimizer.py --hooks      → Muestra hooks virales
"""

import json, random, sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ─── VIRAL HOOKS (primeras líneas que atrapan) ───
HOOKS = [
    # Emotional
    "🔥 Esto cambió mi vida hoy...",
    "😭 Leí esto y no pude contener las lágrimas...",
    "💔 Si estás pasando por algo difícil, esto es para ti...",
    "🙏 Dios me habló con este versículo hoy...",
    
    # Challenge
    "⚠️ El 99% de cristianos ignora este versículo...",
    "🤔 ¿Crees que esto es casualidad?",
    "😳 Lo que dice este versículo te va a sorprender...",
    "⏰ 30 segundos que pueden cambiar tu día...",
    
    # Curiosity
    "📖 El versículo más poderoso que casi nadie lee...",
    "🕊️ Esto es lo que Dios quiere decirte HOY...",
    "🔥 Esta palabra es para ti. Sí, para TI.",
    "🙌 No lo vas a creer... pero está en la Biblia.",
    
    # Urgency
    "‼️ No ignores esto hoy...",
    "⏳ Mensaje urgente para ti...",
    "🔔 Dios tiene algo que decirte AHORA...",
    
    # Community
    "👥 Comparte esto con quien necesite escucharlo...",
    "💬 Comenta AMÉN si crees en el poder de Dios...",
    "👇 Etiqueta a 3 personas que necesiten esta palabra...",
]

# ─── VIRAL CTAs (Call to Action, al final) ───
CTAs = [
    "❤️ Dale LIKE si Dios te habló hoy",
    "💬 Comenta tu versículo favorito abajo",
    "↗️ COMPARTE esta palabra — podrías cambiar el día de alguien",
    "🙏 Escribe AMÉN si crees en los milagros",
    "👇 Etiqueta a un amigo que necesite escuchar esto",
    "🔥 Síguenos para recibir la palabra de Dios cada día",
    "⏰ Activa las notificaciones para no perderte ningún mensaje",
    "📲 Guarda este post para volver a leerlo cuando lo necesites",
    "💪 Comenta 'YO' si vas a confiar en Dios hoy pase lo que pase",
    "🕊️ Envía esto por DM a alguien que esté pasando por un momento difícil",
]

# ─── TRENDING HASHTAG SETS (rotativos por día de semana) ───
HASHTAG_SETS = {
    "broad": [
        "#Viral #FYP #Parati #Trending #Explorar #ReelsFacebook #ViralCristiano",
        "#Viral #Reels #ParaTi #Tendencia #DiosEsAmor #FeViral",
        "#FYPシ #Viral2026 #Dios #CristoVive #Fe #Milagros #Trending",
        "#ExplorePage #Viral #ReelsInstagram #CristianosUnidos #JesusLives",
    ],
    "niche": [
        "#JesusDaily #FeCristiana #Biblia #Oracion #VidaCristiana #CristoRey",
        "#PalabraDeDios #Devocional #Cristianos #Iglesia #DiosEsBueno",
        "#Fe #Esperanza #AmorDeDios #OracionDiaria #SantoRosario",
    ],
    "growth": [
        "#CristianosEnFacebook #ComunidadCristiana #JovenesCristianos",
        "#LatinosCristianos #CristianosUnidos #FeCatolica #Evangelio",
    ],
    "seasonal": {
        # Current month (June 2026)
        6: "#JunioConFe #MitadDeAño #MesDelSagradoCorazon #VeranoConDios",
    }
}

def get_trending_hashtags():
    """Genera set de hashtags optimizado para viralidad."""
    day = datetime.now().weekday()  # 0=Monday, 6=Sunday
    month = datetime.now().month
    
    # Pick 1 broad, 1 niche, 1 growth, 1 seasonal
    broad = random.choice(HASHTAG_SETS["broad"])
    niche = random.choice(HASHTAG_SETS["niche"])
    growth = random.choice(HASHTAG_SETS["growth"])
    seasonal = HASHTAG_SETS["seasonal"].get(month, "")
    
    return f"{broad} {niche} {growth} {seasonal}"

def get_random_hook():
    return random.choice(HOOKS)

def get_random_cta():
    return random.choice(CTAs)

def optimize_caption(post, video=False):
    """Optimiza un caption para viralidad."""
    hook = get_random_hook()
    cta = get_random_cta()
    hashtags = get_trending_hashtags()
    
    verse = post.get("verse", "")
    ref = post.get("reference", "")
    reflection = post.get("reflection", "")
    
    if video:
        # Video/Reel caption (corto, directo)
        caption = f"""{hook}

"{verse}"
— {ref}

{reflection}

{cta}

{hashtags}
#JesusDaily #CristoEsRey 🕊️🔥"""
    else:
        # Image caption
        caption = f"""{hook}

"{verse}"
— {ref}

{reflection}

💬 ¿Qué te dice Dios hoy a través de esta palabra? Cuéntame en los comentarios.

{cta}

{hashtags}
#JesusDaily #Fe #Biblia #CristoEsRey ✝️"""
    
    return caption.strip()

def optimize_video_caption(title, video=False):
    """Caption para videos/Reels — ultra corto y viral."""
    hook = get_random_hook()
    cta = random.choice([
        "🔥 Síguenos para más videos como este",
        "🙏 Comenta AMÉN si crees",
        "↗️ Comparte este Reel — Dios te usará",
        "❤️ Dale like si este mensaje tocó tu corazón",
    ])
    hashtags = get_trending_hashtags()
    
    return f"""{hook}

📖 {title}

{cta}

{hashtags} #JesusDaily #ShortsCristianos"""

def cmd_optimize(day):
    """Optimiza un post existente."""
    posts_file = BASE_DIR / "posts.json"
    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)
    
    idx = day - 1
    if idx >= len(posts):
        print(f"❌ Día máximo: {len(posts)}")
        return
    
    post = posts[idx]
    original = f"""🙏 {post.get('category','fe')} | DÍA {post['day']}

"{post['verse']}"
— {post['reference']}

{post['reflection']}"""
    
    optimized = optimize_caption(post)
    
    print("═══════════ ORIGINAL ═══════════")
    print(original[:300] + "...")
    print("\n═══════════ VIRAL OPTIMIZADO ═══════════")
    print(optimized[:500])
    print(f"\n📊 Longitud: {len(original)} → {len(optimized)} chars")

def cmd_hooks():
    print("🎣 HOOKS VIRALES (para abrir posts):\n")
    for i, h in enumerate(HOOKS, 1):
        print(f"  {i}. {h}")
    
    print("\n🔄 CTAs (para cerrar posts):\n")
    for i, c in enumerate(CTAs, 1):
        print(f"  {i}. {c}")

def cmd_hashtags():
    print("🏷️ HASHTAGS TRENDING (hoy):\n")
    for _ in range(3):
        print(f"  {get_trending_hashtags()}\n")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🎯 VIRAL CONTENT OPTIMIZER — Jesus Daily")
        print("=" * 50)
        print(f"\n🎣 Hook del día:\n   {get_random_hook()}")
        print(f"\n🔄 CTA del día:\n   {get_random_cta()}")
        print(f"\n🏷️ Hashtags trending:\n   {get_trending_hashtags()}")
        print("\nUso: python3 viral_optimizer.py [--post N|--hooks|--hashtags]")
    elif sys.argv[1] == "--post" and len(sys.argv) > 2:
        cmd_optimize(int(sys.argv[2]))
    elif sys.argv[1] == "--hooks":
        cmd_hooks()
    elif sys.argv[1] == "--hashtags":
        cmd_hashtags()
    else:
        print("Uso: python3 viral_optimizer.py [--post N|--hooks|--hashtags]")
