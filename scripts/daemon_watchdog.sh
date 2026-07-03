#!/usr/bin/env bash
# ==============================================================================
# 🎖️ DÉMON WATCHDOG DRACONIEN — ARVEA NATURE AUTOMATION ENGINE
# Surveille, protège et ressuscite le bot Telegram et les files d'attente 24/7.
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BOT_SCRIPT="$PROJECT_ROOT/bot_telegram/bot.py"
LOG_FILE="$PROJECT_ROOT/gestion_prospects/watchdog.log"
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    VENV_PYTHON="python3"
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] 🛡️ Lancement du Watchdog Draconien Arvea Nature..." | tee -a "$LOG_FILE"

# 1. Activation du verrouillage d'énergie Termux (Anti-Sleep)
if command -v termux-wake-lock &> /dev/null; then
    termux-wake-lock
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Verrouillage Wake-Lock Termux activé." | tee -a "$LOG_FILE"
fi

# 2. Boucle de surveillance immortelle
while true; do
    # Vérifier si le bot tourne
    if ! pgrep -f "$BOT_SCRIPT" > /dev/null; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ ALERTE : Bot arrêté ou tué par l'OS ! Résurrection immédiate..." | tee -a "$LOG_FILE"
        cd "$PROJECT_ROOT" && "$VENV_PYTHON" "$BOT_SCRIPT" >> "$PROJECT_ROOT/gestion_prospects/bot_engine.log" 2>&1 &
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] 🔄 Bot ressuscité avec le PID : $!" | tee -a "$LOG_FILE"
    fi

    # Vérification d'intégrité de la base SQLite
    DB_PATH="$PROJECT_ROOT/gestion_prospects/arvea_automation.db"
    if [ -f "$DB_PATH" ]; then
        CHECK=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;")
        if [ "$CHECK" != "ok" ]; then
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] 🚨 ERREUR CRITIQUE : Corruption SQLite détectée ($CHECK)!" | tee -a "$LOG_FILE"
        fi
    fi

    sleep 10
done
