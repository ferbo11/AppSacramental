#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "No existe .env. Ejecute primero: cp .env.example .env"
    exit 1
fi

if ! docker compose ps --all --services | grep -qx web; then
    echo "El contenedor web no existe todavia."
    echo "Ejecute primero: docker compose up -d --build"
    exit 1
fi

echo "Este script copiara los archivos locales dentro de los volumenes"
echo "de Docker y reemplazara los datos que ya existan alli."
echo "Los archivos originales del equipo NO se modifican."
echo
read -r -p "Desea continuar? [s/N] " respuesta

case "$respuesta" in
    s|S|si|SI|sí|SÍ) ;;
    *) echo "Operacion cancelada."; exit 0 ;;
esac

docker compose stop web >/dev/null 2>&1 || true

if [ -f agenda.sqlite3 ]; then
    echo "Copiando agenda.sqlite3..."
    docker compose cp agenda.sqlite3 web:/data/agenda.sqlite3
else
    echo "Aviso: no se encontro agenda.sqlite3; se omite."
fi

if [ -f historial.sqlite3 ]; then
    echo "Copiando historial.sqlite3..."
    docker compose cp historial.sqlite3 web:/data/historial.sqlite3
else
    echo "Aviso: no se encontro historial.sqlite3; se omite."
fi

if [ -d media ] && [ -n "$(find media -type f -print -quit)" ]; then
    echo "Copiando archivos multimedia..."
    docker compose cp media/. web:/app/media/
else
    echo "Aviso: no se encontraron archivos en media/; se omite."
fi

echo "Ajustando permisos de los volumenes..."
docker compose run --rm --no-deps -u root --entrypoint sh web \
    -c 'chown -R appuser:appuser /data /app/media'

docker compose start web

echo "Datos locales copiados. Revise los logs con:"
echo "  docker compose logs -f web"
