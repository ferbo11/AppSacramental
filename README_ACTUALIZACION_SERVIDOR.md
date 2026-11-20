# Actualización del servidor de SacraNet

Esta guía describe cómo actualizar SacraNet en el servidor utilizando Docker Compose, sin tocar la base de datos ni los volúmenes existentes.

## 1. Preparación

Entrar al directorio del proyecto:

```bash
cd /ruta/al/proyecto/AppSacramental
```

Verificar el estado de Git. No debe haber cambios propios sin guardar:

```bash
git status
```

Identificar la rama que contiene los cambios:

```bash
git branch --show-current
```

La rama utilizada para esta actualización es:

```text
master
```

Si el servidor está en otra rama, no la reemplace sin antes confirmar con el responsable del sistema.

## 2. Respaldo

Antes de actualizar, generar un respaldo de PostgreSQL:

```bash
mkdir -p "$HOME/respaldos_sacranet"
ARCHIVO="$HOME/respaldos_sacranet/SACRANET_BD_$(date +%Y%m%d_%H%M%S).dump"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$ARCHIVO"
```

Verificar que el respaldo se haya generado correctamente:

```bash
ls -lh "$ARCHIVO"
docker compose exec -T db pg_restore -l < "$ARCHIVO" >/dev/null && echo "Respaldo válido"
```

No elimine ni sobrescriba este respaldo. No reemplace la base de datos existente por otra.

## 3. Descargar cambios

```bash
git fetch origin
git pull origin master
```

Si `git pull` reporta conflictos, detenga el proceso y avise al responsable. No fuerce el pull.

## 4. Actualizar Docker

Reconstruir y levantar los servicios:

```bash
docker compose up -d --build
```

No ejecute `docker compose down -v`, `docker volume rm` ni ningún comando que elimine volúmenes o datos.

## 5. Verificaciones

Comprobar que los tres servicios estén activos:

```bash
docker compose ps
```

Revisar los registros del servicio web:

```bash
docker compose logs --tail=100 web
```

Verificar la configuración de Django:

```bash
docker compose exec web python manage.py check
```

Verificar el acceso web mediante Nginx. Según el puerto configurado en `.env` (`HTTP_PORT`, 80 por defecto):

```bash
curl -I http://localhost/
```

También puede abrir `http://localhost/` en un navegador y confirmar que aparece la pantalla de inicio de SacraNet.

No modifique `.env` durante esta verificación.

## 6. Reversión

Si la actualización falla, primero identifique el commit anterior:

```bash
git log --oneline -5
```

Guarde el hash del commit al que desea volver y ejecute:

```bash
git reset --hard <HASH_DEL_COMMIT_ANTERIOR>
docker compose up -d --build
```

Después repita las verificaciones de la sección 5.

No elimine volúmenes de Docker. No ejecute `docker compose down -v`. La base de datos y los archivos de constancias deben permanecer intactos.

Solo si existe una falla confirmada de datos y con autorización explícita, utilice el respaldo de la sección 2. No reemplace la base de datos de forma rutinaria.

## 7. Consideraciones

- No modificar el archivo `.env`.
- No eliminar volúmenes de Docker.
- No ejecutar migraciones sin comprobar antes si son necesarias.
- No reemplazar la base de datos.
- No modificar la configuración de red del servidor.
- No ejecutar `git push --force`.
- Conservar los respaldos generados hasta confirmar que la actualización es estable.
