#!/usr/bin/env bash
# Database backup (leads live there): sudo bash deploy/backup.sh
# Writes backups/temir-YYYY-MM-DD-HHMM.sql.gz next to the project and keeps the last 14.
# For a daily backup at 03:00 add to root's crontab (sudo crontab -e):
#   0 3 * * * bash /opt/temir-gidro/deploy/backup.sh >/dev/null 2>&1
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
COMPOSE=(docker compose -f compose.yml -f deploy/compose.prod.yml)

"${COMPOSE[@]}" ps --status running --services 2>/dev/null | grep -qx db || { echo ">>> База не запущена — пропускаю бэкап"; exit 0; }

mkdir -p backups
FILE="backups/temir-$(date +%Y-%m-%d-%H%M).sql.gz"
"${COMPOSE[@]}" exec -T db pg_dump -U temir temir | gzip > "$FILE"
chmod 600 "$FILE"
ls -1t backups/temir-*.sql.gz | tail -n +15 | xargs -r rm --
echo ">>> Бэкап базы: $FILE"
# Restore: gunzip -c FILE | docker compose -f compose.yml -f deploy/compose.prod.yml exec -T db psql -U temir temir
