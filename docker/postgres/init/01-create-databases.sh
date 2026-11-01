#!/bin/bash
set -euo pipefail

# Crea las bases adicionales dentro de la misma instancia PostgreSQL.
# Se ejecuta una sola vez, cuando el volumen postgres_data esta vacio.

for db in agenda historial; do
    exists="$(
        psql \
            --username "$POSTGRES_USER" \
            --dbname postgres \
            --tuples-only \
            --no-align \
            --command "SELECT 1 FROM pg_database WHERE datname = '$db'"
    )"

    if [ "$exists" != "1" ]; then
        echo "Creando base de datos adicional: $db"
        psql \
            --username "$POSTGRES_USER" \
            --dbname postgres \
            --command "CREATE DATABASE \"$db\" OWNER \"$POSTGRES_USER\""
    else
        echo "La base de datos $db ya existe."
    fi
done
