#!/bin/bash
set -euo pipefail

# Importacion inicial opcional.
#
# Coloque el respaldo en docker/postgres/init/ antes del primer
# docker compose up. El script solo se ejecuta cuando el volumen
# postgres_data esta vacio, por lo que no sobrescribe datos existentes.

DUMP_CUSTOM=""
DUMP_SQL=""

for candidate in \
    /docker-entrypoint-initdb.d/SACRANET_BD.dump \
    /docker-entrypoint-initdb.d/SACRANET_BD.backup; do
    if [ -f "$candidate" ]; then
        DUMP_CUSTOM="$candidate"
        break
    fi
done

for candidate in \
    /docker-entrypoint-initdb.d/SACRANET_BD.sql \
    /docker-entrypoint-initdb.d/Sacranet_BD.sql; do
    if [ -f "$candidate" ]; then
        DUMP_SQL="$candidate"
        break
    fi
done

if [ -n "$DUMP_CUSTOM" ]; then
    echo "Restaurando respaldo PostgreSQL: $DUMP_CUSTOM"
    pg_restore \
        --username "$POSTGRES_USER" \
        --dbname "$POSTGRES_DB" \
        --no-owner \
        --no-privileges \
        --exit-on-error \
        "$DUMP_CUSTOM"
    echo "Respaldo restaurado correctamente."
elif [ -n "$DUMP_SQL" ]; then
    echo "Restaurando respaldo SQL: $DUMP_SQL"
    psql \
        --username "$POSTGRES_USER" \
        --dbname "$POSTGRES_DB" \
        --set ON_ERROR_STOP=1 \
        --file "$DUMP_SQL"
    echo "Respaldo SQL restaurado correctamente."
else
    echo "No se encontro respaldo inicial; se usara una base vacia."
fi
