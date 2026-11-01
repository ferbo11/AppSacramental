#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "No existe .env. Ejecute primero: cp .env.example .env"
    exit 1
fi

mkdir -p backups

fecha="$(date +%Y%m%d_%H%M%S)"
archivo="backups/SACRANET_BD_${fecha}.dump"

echo "Generando respaldo en ${archivo}..."
docker compose exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' \
    > "$archivo"

echo "Respaldo completado: ${archivo}"
