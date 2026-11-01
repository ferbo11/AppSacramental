#!/bin/sh
set -eu

DB_ENGINE="${DB_ENGINE:-postgresql}"

if [ "$DB_ENGINE" = "postgresql" ] || [ "$DB_ENGINE" = "postgres" ]; then
    echo "Esperando a que PostgreSQL este disponible..."

    python - <<'PY'
import os
import sys
import time

import psycopg

host = os.environ.get("DB_HOST", "db")
port = os.environ.get("DB_PORT", "5432")
user = os.environ.get("DB_USER") or os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD", "")
dbname = os.environ.get("DB_NAME") or os.environ.get("POSTGRES_DB", "SACRANET_BD")

intentos = int(os.environ.get("DB_WAIT_RETRIES", "60"))
espera = int(os.environ.get("DB_WAIT_SECONDS", "2"))

for intento in range(1, intentos + 1):
    try:
        with psycopg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=3,
        ):
            print("PostgreSQL disponible.")
            sys.exit(0)
    except Exception as exc:
        print(f"PostgreSQL no disponible ({intento}/{intentos}): {exc}")
        time.sleep(espera)

print("No fue posible conectar con PostgreSQL.", file=sys.stderr)
sys.exit(1)
PY
fi

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    echo "Aplicando migraciones de la base principal..."
    python manage.py migrate --noinput

    echo "Aplicando migraciones de la base agenda..."
    python manage.py migrate --database=agenda --noinput

    echo "Aplicando migraciones de la base historial..."
    python manage.py migrate --database=historial --noinput
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
    echo "Recolectando archivos estaticos..."
    python manage.py collectstatic --noinput
fi

echo "Iniciando Gunicorn..."
exec "$@"
