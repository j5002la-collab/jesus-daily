# ✝️ JESUS DAILY — Guía de Operación

Automatización de publicaciones cristianas/católicas en Facebook con monetización integrada.

---

## 🎯 OBJETIVO: $2,000/mes

### Fuentes de ingreso planificadas

| Fuente | Meta mensual | Requisitos |
|--------|-------------|------------|
| **Facebook Reels monetization** | $800-1,200 | 10K seguidores + 600K minutos en 60 días |
| **Amazon Afiliados** (Biblias, libros) | $400-800 | Cuenta Amazon Associates activa |
| **Gumroad** (Devocionales PDF) | $200-400 | Productos digitales publicados |
| **YouTube Shorts monetization** | $200-400 | 1K subs + 10M views en 90 días |

---

## 📦 Estructura del Proyecto

```
jesus-daily/
├── posts.json           ← Banco de 500 mensajes (rota infinitamente)
├── scheduler.py         ← Control de publicaciones (next, publish, status...)
├── fb_publisher.py      ← Publica imagen + caption en Facebook
├── daily_publish.py     ← Script para cron (sin interacción)
├── operacion.py         ← Orquestador (daily, weekly, revenue tracking)
├── .env                 ← Credenciales (NO SE SUBE A GIT)
├── .env.example         ← Template de credenciales
├── .gitignore           ← Protege .env, state, logs
├── images/              ← Imágenes generadas (PNG)
├── output/              ← Posts para copia manual
├── logs/                ← Historial de operación
├── productos/           ← PDFs para Gumroad
└── GUIA.md              ← Esta guía
```

---

## 🚀 Instalación

### 1. Clonar el repo
```bash
git clone https://github.com/j5002la-collab/jesus-daily.git
cd jesus-daily
```

### 2. Configurar Facebook
```bash
cp .env.example .env
nano .env  # Agregar FB_PAGE_ID y FB_ACCESS_TOKEN
```

### 3. Probar
```bash
python3 scheduler.py next     # Ver el mensaje de hoy
python3 scheduler.py status   # Ver estado
python3 scheduler.py publish  # Publicar en Facebook
```

### 4. Configurar cron (automático diario 9 AM)
```bash
crontab -e
# Agregar:
0 9 * * * cd /opt/data/jesus-daily && python3 daily_publish.py
```

---

## 📱 Facebook Page Setup

1. Crear página: "Jesus Daily" (o nombre similar)
2. Categoría: Organización religiosa / Iglesia
3. Crear Facebook App en developers.facebook.com (tipo: Business)
4. Obtener Token de Página con permisos:
   - pages_manage_posts
   - pages_read_engagement
   - pages_show_list
5. Intercambiar por token larga duración (60 días)

---

## 💰 PLAN DE MONETIZACIÓN (Ruta a $2K/mes)

### FASE 1: Audiencia (Mes 1-2) — $0
- Publicar diariamente contenido de valor
- 500 mensajes rotando = 16 meses sin repetir
- Meta: 1,000-2,000 seguidores
- Estrategia: contenido orgánico + compartir en grupos católicos/cristianos

### FASE 2: Afiliados (Mes 2-3) — $100-300/mes
- Crear cuenta Amazon Associates
- Recomendar Biblias, devocionales, rosarios
- Links en cada 3er post (no saturar)
- Productos sugeridos:
  - Biblia de Jerusalén (~$25)
  - Catecismo de la Iglesia Católica (~$15)
  - Rosario de madera (~$10)
  - Mi Cristo Roto (libro) (~$12)

### FASE 3: Productos digitales (Mes 3-4) — $300-500/mes
- Crear 3 devocionales PDF en Gumroad ($7-12 c/u)
  - "30 Días de Fe" — Devocional mensual
  - "Oraciones que Transforman" — Guía de oración
  - "El Poder del Rosario" — Guía ilustrada
- Promocionar en posts cada 7 días

### FASE 4: Monetización nativa (Mes 4-6) — $1,000-1,500/mes
- Facebook Reels: Subir shorts del canal YouTube
- Requisito: 10K seguidores + 600K minutos vistos
- YouTube Shorts: 1K subs + 10M views
- Ingresos por views en ambas plataformas

### FASE 5: Escala (Mes 6+) — $2,000+/mes
- Múltiples fuentes combinadas
- Email list para devocionales diarios
- Comunidad premium (Patreon, Telegram)
- Más productos digitales (cursos, webinars)

---

## 🤖 Automatización YouTube → Facebook

Para cross-postear Shorts de @JesusDailyShorts1 a Facebook:

```bash
# Instalar yt-dlp
pip install yt-dlp

# Descargar último short
python3 crosspost.py
```

El script `crosspost.py`:
1. Descarga el último short del canal
2. Lo formatea para Facebook Reels (9:16 vertical)
3. Lo sube como Reel nativo a Facebook
4. Registra en el log para no duplicar

---

## 📊 Comandos Rápidos

| Comando | Descripción |
|---------|-------------|
| `python3 scheduler.py next` | Ver mensaje de hoy |
| `python3 scheduler.py publish` | Publicar en Facebook |
| `python3 scheduler.py status` | Estado del ciclo |
| `python3 scheduler.py list` | Listar todos los posts |
| `python3 operacion.py daily` | Ejecutar rutina diaria |
| `python3 operacion.py weekly` | Reporte semanal |
| `python3 operacion.py status` | Estado general |
| `python3 operacion.py revenue 25` | Registrar $25 de ingreso |

---

## ⚠️ Mantenimiento

- **Token de Facebook**: Expira cada ~60 días. Renovar antes.
- **Ciclos de contenido**: 500 días (16 meses). Luego se reinicia automáticamente.
- **Backup**: Hacer git push después de cada cambio importante.

---

## 🔗 Enlaces Útiles

- Facebook Developers: https://developers.facebook.com
- Graph API Explorer: https://developers.facebook.com/tools/explorer
- Amazon Afiliados: https://afiliados.amazon.com
- Gumroad: https://gumroad.com
- Canal YouTube: https://www.youtube.com/@JesusDailyShorts1
