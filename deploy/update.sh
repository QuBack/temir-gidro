#!/usr/bin/env bash
# Update the site on the server to the latest code: sudo bash deploy/update.sh
# Makes a database backup first, then pulls, rebuilds and restarts.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
COMPOSE=(docker compose -f compose.yml -f deploy/compose.prod.yml)

bash deploy/backup.sh
echo ">>> Забираю свежий код"
git pull --ff-only
echo ">>> Пересобираю и перезапускаю"
"${COMPOSE[@]}" up -d --build --remove-orphans
docker image prune -f >/dev/null
"${COMPOSE[@]}" ps
