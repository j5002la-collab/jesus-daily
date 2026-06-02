#!/usr/bin/env python3
"""
TRACKER DE MÉTRICAS — Jesus Daily
Lee alcance, engagement y views de Facebook.
Guarda snapshot diario en metrics.json para dashboard y reportes.

Uso:
  python3 tracker.py           → Snapshot diario
  python3 tracker.py --post ID → Métricas de un post específico
  python3 tracker.py --page    → Solo métricas de página
  python3 tracker.py --history → Últimos 7 días
"""

import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
METRICS_FILE = BASE_DIR / "metrics.json"
STATE_FILE = BASE_DIR / "estado_operacion.json"
REVENUE_FILE = BASE_DIR / "revenue.json"

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

def api_get(endpoint, token, params=""):
    """Hace GET a la Graph API."""
    sep = "&" if "?" in endpoint else "?"
    url = f"https://graph.facebook.com/v19.0/{endpoint}{sep}access_token={token}{params}"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read()).get('error', {}).get('message', str(e))}
    except Exception as e:
        return {"error": str(e)}

def get_page_metrics(page_id, token):
    """Obtiene métricas de la página."""
    print("📊 Obteniendo métricas de página...")
    
    # Basic page info
    fields = "name,followers_count,fan_count,new_like_count"
    page = api_get(f"{page_id}", token, f"&fields={fields}")
    
    if "error" in page:
        print(f"  ❌ {page['error']}")
        return {}
    
    # Page insights (requires pages_read_engagement)
    insights_fields = "page_impressions,page_engaged_users,page_follows,page_views_total"
    metrics = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "page_name": page.get("name", "?"),
        "followers": int(page.get("followers_count", 0)),
        "likes": int(page.get("fan_count", 0)),
    }
    
    # Try to get insights
    insights = api_get(f"{page_id}/insights", token, 
                       f"&metric={insights_fields}&period=day")
    
    if "data" in insights:
        for item in insights["data"]:
            name = item.get("name", "")
            values = item.get("values", [])
            if values:
                val = values[-1].get("value", 0)
                if "impressions" in name:
                    metrics["impressions_today"] = val
                elif "engaged_users" in name:
                    metrics["engaged_users_today"] = val
                elif "follows" in name:
                    metrics["follows_today"] = val
                elif "views_total" in name:
                    metrics["page_views_today"] = val
    
    print(f"  👥 {metrics['followers']} seguidores")
    print(f"  📈 +{metrics.get('follows_today', '?')} hoy")
    print(f"  👁️ {metrics.get('impressions_today', '?')} impresiones")
    
    return metrics

def get_post_metrics(post_id, token):
    """Obtiene métricas de un post específico."""
    fields = "reactions.summary(true),comments.summary(true),shares,insights.metric(post_impressions,post_engaged_users,post_video_views)"
    data = api_get(post_id, token, f"&fields={fields}")
    
    if "error" in data:
        return {"error": data["error"]}
    
    reactions = data.get("reactions", {}).get("summary", {}).get("total_count", 0)
    comments = data.get("comments", {}).get("summary", {}).get("total_count", 0)
    shares = data.get("shares", {}).get("count", 0)
    
    post_metrics = {
        "reactions": reactions,
        "comments": comments,
        "shares": shares,
        "engagement": reactions + comments + shares,
    }
    
    # Insights
    insights = data.get("insights", {}).get("data", [])
    for item in insights:
        name = item.get("name", "")
        vals = item.get("values", [])
        if vals:
            v = vals[0].get("value", 0)
            if "impressions" in name:
                post_metrics["impressions"] = v
            elif "engaged_users" in name:
                post_metrics["engaged_users"] = v
            elif "video_views" in name:
                post_metrics["video_views"] = v
    
    return post_metrics

def get_recent_posts(page_id, token, limit=10):
    """Obtiene posts recientes con métricas."""
    fields = "id,message,created_time,permalink_url,reactions.summary(true),comments.summary(true),shares"
    data = api_get(f"{page_id}/feed", token, 
                   f"&fields={fields}&limit={limit}")
    
    posts = []
    if "data" in data:
        for p in data["data"]:
            msg = (p.get("message") or "")[:60]
            posts.append({
                "id": p.get("id"),
                "message": msg,
                "created": p.get("created_time"),
                "url": p.get("permalink_url", ""),
                "reactions": p.get("reactions", {}).get("summary", {}).get("total_count", 0),
                "comments": p.get("comments", {}).get("summary", {}).get("total_count", 0),
                "shares": p.get("shares", {}).get("count", 0),
            })
    return posts

def cmd_track(page_id=None, token=None):
    """Snapshot diario completo."""
    env = load_env()
    pid = page_id or env.get("FB_PAGE_ID", "")
    tok = token or env.get("FB_ACCESS_TOKEN", "")
    
    if not pid or not tok:
        print("❌ Sin credenciales")
        return
    
    print(f"📊 TRACKER JESUS DAILY — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 1. Page metrics
    metrics = get_page_metrics(pid, tok)
    
    # 2. Recent posts performance
    print("\n📝 Posts recientes:")
    posts = get_recent_posts(pid, tok, 10)
    total_engagement = 0
    total_reactions = 0
    
    for i, p in enumerate(posts[:5]):
        eng = p["reactions"] + p["comments"] + p["shares"]
        total_engagement += eng
        total_reactions += p["reactions"]
        print(f"  {i+1}. ❤️{p['reactions']} 💬{p['comments']} ↗️{p['shares']} | {p['message'][:50]}")
    
    metrics["posts_analyzed"] = len(posts)
    metrics["total_engagement_10posts"] = total_engagement
    metrics["total_reactions_10posts"] = total_reactions
    metrics["engagement_rate"] = round(total_engagement / max(metrics["followers"], 1) * 100, 2)
    
    print(f"\n  📊 Engagement rate: {metrics['engagement_rate']}%")
    
    # 3. Save to history
    history = []
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            history = json.load(f)
    
    history.append(metrics)
    # Keep last 90 days
    history = history[-90:]
    
    with open(METRICS_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Snapshot guardado ({len(history)} días de historia)")
    
    # 4. Growth calculation
    if len(history) >= 2:
        prev = history[-2]
        growth = metrics["followers"] - prev.get("followers", 0)
        print(f"📈 Crecimiento hoy: {'+' if growth >= 0 else ''}{growth} seguidores")
        
        if len(history) >= 7:
            week_ago = history[-8]
            week_growth = metrics["followers"] - week_ago.get("followers", 0)
            print(f"📈 Crecimiento 7 días: {'+' if week_growth >= 0 else ''}{week_growth}")
            
            # Projections
            daily_avg = week_growth / 7
            if daily_avg > 0:
                to_1k = max(0, int((1000 - metrics["followers"]) / daily_avg))
                to_10k = max(0, int((10000 - metrics["followers"]) / daily_avg))
                print(f"🎯 Proyección 1K seguidores: {to_1k} días")
                print(f"🎯 Proyección 10K seguidores (monetizar Reels): {to_10k} días")
    
    return metrics

def cmd_post(post_id, token=None):
    """Métricas de un post."""
    env = load_env()
    tok = token or env.get("FB_ACCESS_TOKEN", "")
    
    m = get_post_metrics(post_id, tok)
    if "error" in m:
        print(f"❌ {m['error']}")
        return
    
    print(f"\n📊 Post: {post_id}")
    print(f"  👁️ Impresiones: {m.get('impressions', '?')}")
    print(f"  👥 Engaged: {m.get('engaged_users', '?')}")
    print(f"  ▶️ Video views: {m.get('video_views', '?')}")
    print(f"  ❤️ Reacciones: {m.get('reactions', 0)}")
    print(f"  💬 Comentarios: {m.get('comments', 0)}")
    print(f"  ↗️ Compartido: {m.get('shares', 0)}")
    print(f"  🔥 Engagement total: {m.get('engagement', 0)}")

def cmd_history():
    """Últimos 7 días de métricas."""
    if not METRICS_FILE.exists():
        print("❌ No hay datos históricos")
        return
    
    with open(METRICS_FILE) as f:
        history = json.load(f)
    
    print(f"\n📈 ÚLTIMOS {min(7, len(history))} DÍAS\n")
    print(f"{'Fecha':<12} {'Seguidores':<12} {'+Día':<8} {'Impresiones':<12} {'EngRate':<8}")
    print("-" * 55)
    
    for i, h in enumerate(history[-7:]):
        date = h.get("date", "?")
        followers = h.get("followers", 0)
        impressions = h.get("impressions_today", "?")
        eng_rate = h.get("engagement_rate", 0)
        
        # Daily growth
        growth = ""
        if i > 0:
            prev_f = history[-(8-i)] if len(history) >= (8-i) else None
            if prev_f:
                diff = followers - prev_f.get("followers", followers)
                growth = f"+{diff}" if diff > 0 else str(diff)
        
        print(f"{date:<12} {followers:<12} {growth:<8} {str(impressions):<12} {eng_rate}%")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        cmd_track()
    elif sys.argv[1] == "--post" and len(sys.argv) > 2:
        cmd_post(sys.argv[2])
    elif sys.argv[1] == "--page":
        env = load_env()
        get_page_metrics(env.get("FB_PAGE_ID", ""), env.get("FB_ACCESS_TOKEN", ""))
    elif sys.argv[1] == "--history":
        cmd_history()
    else:
        print("Uso: python3 tracker.py [--post ID|--page|--history]")
