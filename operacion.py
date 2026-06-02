#!/usr/bin/env python3
"""
✝️ OPERACIÓN JESUS DAILY — Orquestador
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ejecuta y monitorea toda la operación:
  1. Publicación diaria (fb_publisher.py)
  2. Tracking de métricas
  3. Reportes semanales
  4. Revenue tracking ($2K meta)
  5. Logs centralizados

Uso:
  python3 operacion.py daily      → Ejecuta tareas diarias
  python3 operacion.py weekly     → Reporte semanal
  python3 operacion.py status     → Estado general
  python3 operacion.py revenue N  → Registra ingreso ($N)
"""
import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "estado_operacion.json"
REVENUE_FILE = BASE_DIR / "revenue.json"
METRICS_FILE = BASE_DIR / "metrics.json"
LOG_DIR = BASE_DIR / "logs"
REPORTES_DIR = BASE_DIR / "reportes"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORTES_DIR, exist_ok=True)

META_MENSUAL = 2000  # USD


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_file = LOG_DIR / f"operacion_{datetime.now().strftime('%Y%m')}.log"
    with open(log_file, "a") as f:
        f.write(line + "\n")


def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_script(script_name, timeout=120):
    path = BASE_DIR / script_name
    if not path.exists():
        log(f"❌ Script no encontrado: {script_name}", "ERROR")
        return None
    try:
        result = subprocess.run(
            ["python3", str(path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(BASE_DIR)
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "TIMEOUT", "success": False}
    except Exception as e:
        return {"exit_code": -1, "stdout": "", "stderr": str(e), "success": False}


def cmd_daily():
    log("═══ INICIO OPERACIÓN DIARIA ═══")

    state = load_json(STATE_FILE, {
        "days_running": 0,
        "total_posts": 0,
        "total_errors": 0,
        "last_daily": None,
        "last_weekly": None,
        "total_revenue_usd": 0,
        "started_at": datetime.now().isoformat()
    })

    # 1. Publicar
    log("📤 Publicando mensaje del día...")
    pub_result = run_script("fb_publisher.py")
    if pub_result and pub_result["success"] and "PUBLICADO" in pub_result["stdout"]:
        log("   ✅ Publicación exitosa")
        state["total_posts"] += 1
    elif pub_result:
        log(f"   ⚠️ Publicación: {pub_result['stderr'][:200] or pub_result['stdout'][:200]}")
        state["total_errors"] += 1
    else:
        log("   ❌ Error ejecutando fb_publisher.py")
        state["total_errors"] += 1

    # 2. Trackear métricas
    log("📊 Recolectando métricas...")
    track_result = run_script("tracker.py")
    if track_result and track_result["success"]:
        log("   ✅ Métricas actualizadas")
    else:
        log("   ⚠️ Tracker: sin datos de insights", "WARN")

    # 3. Update state
    state["days_running"] += 1
    state["last_daily"] = datetime.now().isoformat()
    save_json(STATE_FILE, state)

    # 3. Summary
    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})
    
    # Calculate monthly revenue
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    month_revenue = sum(
        t.get("amount", 0) for t in revenue.get("transactions", [])
        if t.get("date", "") >= month_start
    )

    print(f"""
═══ RESUMEN DIARIO ═══
📅 Día {state['days_running']} de operación
📤 Posts publicados: {state['total_posts']}
💰 Revenue del mes: ${month_revenue:.2f}
💰 Revenue total: ${revenue.get('total', 0):.2f}
🎯 Meta $2K/mes: {month_revenue / META_MENSUAL * 100:.0f}%
❌ Errores: {state['total_errors']}
═══
""")

    return True


def cmd_weekly():
    log("═══ REPORTE SEMANAL ═══")

    state = load_json(STATE_FILE)
    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})

    # Calcular semanal
    week_ago = datetime.now() - timedelta(days=7)
    week_posts = state.get("total_posts", 0)  # posts this week = total - last week total
    
    week_revenue = sum(
        t.get("amount", 0) for t in revenue.get("transactions", [])
        if t.get("date", "") >= week_ago.strftime("%Y-%m-%d")
    )

    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    month_revenue = sum(
        t.get("amount", 0) for t in revenue.get("transactions", [])
        if t.get("date", "") >= month_start
    )

    days_running = state.get("days_running", 0)
    daily_revenue = month_revenue / max(days_running, 1)
    est_monthly = daily_revenue * 30

    report = f"""
╔══════════════════════════════════════════╗
║   ✝️  REPORTE SEMANAL JESUS DAILY      ║
║   {datetime.now().strftime('%Y-%m-%d')}                          ║
╚══════════════════════════════════════════╝

📤 CONTENIDO
   Posts esta semana: {state.get('total_posts', 0)}
   Días operando:     {days_running}
   Errores acumulados: {state.get('total_errors', 0)}

💰 REVENUE
   Esta semana:    ${week_revenue:.2f}
   Este mes:       ${month_revenue:.2f}
   Total acumulado: ${revenue.get('total', 0):.2f}
   
   Estimado mensual: ${est_monthly:.2f}
   Meta $2,000/mes:  {month_revenue / META_MENSUAL * 100:.0f}%
   
   Proyección a 6 meses: ${est_monthly * 6:.2f}
   Proyección a 12 meses: ${est_monthly * 12:.2f}

🎯 MONETIZACIÓN
   Facebook Reels:   Activar monetización (10K seguidores + 600K mins)
   Afiliados Amazon: Biblias, libros, rosarios
   Gumroad:          Devocionales PDF, guías de oración

📦 PRÓXIMOS PASOS
   [ ] Alcanzar 10K seguidores para monetizar Reels
   [ ] Crear cuenta Amazon Afiliados
   [ ] Subir primer devocional PDF a Gumroad
   [ ] Crear landing page con Linktree

╚══════════════════════════════════════════╝
"""
    print(report)

    # Guardar reporte
    report_path = REPORTES_DIR / f"semanal_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_path, "w") as f:
        f.write(report)
    log(f"Reporte guardado: {report_path}")

    state["last_weekly"] = datetime.now().isoformat()
    save_json(STATE_FILE, state)

    return report


def cmd_revenue(amount):
    try:
        amount = float(amount)
    except ValueError:
        log(f"❌ Monto inválido: {amount}", "ERROR")
        return

    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "amount": amount,
        "source": "manual"
    }
    revenue["transactions"].append(transaction)
    revenue["total"] = sum(t["amount"] for t in revenue["transactions"])
    revenue["last_updated"] = datetime.now().isoformat()
    save_json(REVENUE_FILE, revenue)

    # Calcular mensual
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    month_total = sum(
        t.get("amount", 0) for t in revenue["transactions"]
        if t.get("date", "") >= month_start
    )
    
    log(f"💰 Revenue: +${amount:.2f} → Total: ${revenue['total']:.2f} | Mes: ${month_total:.2f} | Meta: {month_total / META_MENSUAL * 100:.0f}%")

    if month_total >= META_MENSUAL:
        log(f"🎉 ¡META DE ${META_MENSUAL}/MES ALCANZADA! 🎉", "MILESTONE")
    elif month_total >= META_MENSUAL * 0.5:
        log(f"📈 ¡50% de la meta mensual!", "MILESTONE")
    elif month_total >= META_MENSUAL * 0.25:
        log(f"📈 25% de la meta mensual", "MILESTONE")


def cmd_status():
    state = load_json(STATE_FILE)
    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})
    sched_state = load_json(BASE_DIR / "state.json")

    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    month_revenue = sum(
        t.get("amount", 0) for t in revenue.get("transactions", [])
        if t.get("date", "") >= month_start
    )

    print(f"""
╔══════════════════════════════╗
║  ✝️ JESUS DAILY — ESTADO   ║
╚══════════════════════════════╝

📅 Días operando:   {state.get('days_running', 0)}
📤 Posts publicados: {state.get('total_posts', 0)}
🔄 Ciclo actual:    Día {sched_state.get('current_day', 0) + 1}/500
❌ Errores:         {state.get('total_errors', 0)}

💰 Revenue mes:     ${month_revenue:.2f}
💰 Revenue total:   ${revenue.get('total', 0):.2f}
🎯 Meta $2K:        {month_revenue / META_MENSUAL * 100:.0f}%

🕐 Último daily:    {state.get('last_daily', 'Nunca')}
📄 Último weekly:   {state.get('last_weekly', 'Nunca')}
""")

    if revenue.get("transactions"):
        print("📋 Últimas transacciones:")
        for t in revenue["transactions"][-5:]:
            print(f"   {t['date']} | ${t['amount']:.2f} | {t.get('source', '?')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 operacion.py [daily|weekly|status|revenue N]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "daily":
        cmd_daily()
    elif cmd == "weekly":
        cmd_weekly()
    elif cmd == "status":
        cmd_status()
    elif cmd == "revenue" and len(sys.argv) > 2:
        cmd_revenue(sys.argv[2])
    else:
        print(f"Comando desconocido: {cmd}")
        print("Uso: python3 operacion.py [daily|weekly|status|revenue N]")
