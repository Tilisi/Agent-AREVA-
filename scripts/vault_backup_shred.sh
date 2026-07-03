#!/usr/bin/env bash
# ==============================================================================
# 🔐 VAULT BACKUP CHIFFRÉ & PROTOCOLE D'AUTODESTRUCTION (SHRED)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_PATH="$PROJECT_ROOT/gestion_prospects/arvea_automation.db"
ENV_PATH="$PROJECT_ROOT/config/.env"

function backup_encrypted() {
    PASSPHRASE_KEY="${1:-ArveaTunisie2026SecureKey}"
    BACKUP_FILE="$PROJECT_ROOT/gestion_prospects/arvea_backup_$(date +%Y%m%d_%H%M%S).db.enc"
    
    if [ -f "$DB_PATH" ]; then
        echo "🔒 Création du snapshot chiffré AES-256..."
        sqlite3 "$DB_PATH" ".backup '/tmp/temp_snapshot.db'"
        openssl enc -aes-256-cbc -salt -pbkdf2 -in "/tmp/temp_snapshot.db" -out "$BACKUP_FILE" -pass pass:"$PASSPHRASE_KEY"
        rm -f "/tmp/temp_snapshot.db"
        echo "✅ Snapshot chiffré généré : $BACKUP_FILE"
    else
        echo "❌ Base de données introuvable."
    fi
}

function panic_shred() {
    echo "⚠️🚨 ACTIVATION DU PROTOCOLE PANIC — DESTRUCTION DES DONNÉES SENSIBLES 🚨⚠️"
    
    # Écrasement militaire en 7 passes (DoD 5220.22-M)
    if [ -f "$ENV_PATH" ]; then
        if command -v shred &> /dev/null; then
            shred -u -z -n 7 "$ENV_PATH"
        else
            dd if=/dev/urandom of="$ENV_PATH" bs=1k count=4 2>/dev/null
            rm -f "$ENV_PATH"
        fi
        echo "💥 Fichier .env pulvérisé."
    fi

    if [ -f "$DB_PATH" ]; then
        if command -v shred &> /dev/null; then
            shred -u -z -n 7 "$DB_PATH"*
        else
            rm -f "$DB_PATH"*
        fi
        echo "💥 Base SQLite pulvérisée."
    fi

    # Tuer tous les processus du bot
    pkill -f "bot_telegram/bot.py"
    pkill -f "daemon_watchdog.sh"
    echo "🛑 Tous les processus ont été terminés. Système neutralisé."
}

case "$1" in
    backup)
        backup_encrypted "$2"
        ;;
    panic)
        panic_shred
        ;;
    *)
        echo "Usage: $0 {backup [passphrase]|panic}"
        exit 1
        ;;
esac
