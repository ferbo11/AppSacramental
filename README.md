# Sacranet - Sistema de Gestión Sacramental

Documentación del proyecto y del despliegue con Docker.

> Última actualización: 31 de octubre de 2026.
>
> `README1.md` se conserva como referencia histórica del avance funcional.
> Este documento describe la arquitectura Docker, la operación y las pruebas realizadas.

---

## 1. Descripción del proyecto

**Sacranet** es una aplicación web para apoyar la administración de los registros
sacramentales de la Parroquia El Calvario, Cobán, Alta Verapaz.

El sistema contempla:

- Registros de Bautismo.
- Registros de Primera Comunión.
- Registros de Confirmación.
- Registros de Matrimonio.
- Emisión y consulta de constancias.
- Agenda parroquial.
- Administración de usuarios y roles.
- Historial de constancias emitidas.
- Reportes y estadísticas.
- Respaldos de información.

> **Nota de documentación:** el Acta de Constitución del proyecto indicaba
> PHP con Laravel como tecnología. La implementación actual está desarrollada
> con **Django/Python**. Esta diferencia debe quedar justificada en la
> documentación académica del proyecto.

---

## 2. Estado del proyecto

**Estado general:** en desarrollo.

La infraestructura Docker fue construida y probada correctamente. La aplicación
responde a través de Nginx, Gunicorn y Django, con PostgreSQL para los datos
principales y SQLite para agenda e historial.

Pruebas realizadas en el entorno Docker:

- Construcción de la imagen sin errores.
- Servicios `db`, `web` y `nginx` en estado `healthy`.
- Restauración del respaldo principal de PostgreSQL.
- Importación de las bases SQLite locales y de los archivos multimedia.
- Inicio de sesión probado con un usuario temporal.
- Acceso correcto a los módulos principales.
- Servicio de archivos estáticos y multimedia desde Nginx.
- Persistencia comprobada después de `docker compose down` y `docker compose up`.

Las funciones de negocio que aún están en ajuste deben seguir probándose según
lo descrito en `README1.md` y en la sección de pruebas de este documento.

---

## 3. Arquitectura de la solución

```text
Navegador
    |
    v
Nginx :80
    |-- /static/  -> volumen static_data
    |-- /media/   -> volumen media_data
    |
    v
Gunicorn :8000
    |
    v
Django
    |-- PostgreSQL: base SACRANET_BD
    |-- SQLite: /data/agenda.sqlite3
    |-- SQLite: /data/historial.sqlite3
```

Características principales:

- Solo Nginx publica un puerto hacia el equipo anfitrión.
- PostgreSQL y Gunicorn quedan en la red interna de Docker.
- Nginx sirve los archivos estáticos y multimedia directamente.
- Gunicorn ejecuta la aplicación Django con workers.
- Los datos se conservan en volúmenes nombrados de Docker.
- El contenedor `web` se ejecuta con un usuario no root (`appuser`, UID 1000).

---

## 4. Tecnologías utilizadas

| Componente | Versión / uso |
| --- | --- |
| Python | 3.12 |
| Django | 6.1 |
| Gunicorn | 23.0.0 |
| PostgreSQL | 18 (`postgres:18-alpine`) |
| SQLite | Agenda e historial |
| Nginx | 1.29 (`nginx:1.29-alpine`) |
| Psycopg | 3.3.6 |
| Pillow | 12.3.0 |
| pypdf | 6.19.0 |
| ReportLab | 5.0.1 |
| Docker | Motor de contenedores |
| Docker Compose | Orquestación de servicios |
| HTML/CSS | Interfaz web |
| Git/GitHub | Control de versiones |

El respaldo `backups/SACRANET_BD.dump` fue generado con PostgreSQL 16.15 y se
restauró correctamente en PostgreSQL 18 usando `pg_restore`.

---

## 5. Requisitos previos

Para ejecutar la aplicación con Docker se necesita:

- Docker Engine o Docker Desktop.
- Docker Compose v2.
- Puerto 80 disponible, o configurar otro puerto con `HTTP_PORT`.
- Al menos 4 GB de memoria RAM recomendados.
- Espacio en disco suficiente para la imagen, PostgreSQL y los archivos multimedia.
- Git para clonar o actualizar el repositorio.

No es necesario instalar Python, Django ni PostgreSQL en el equipo anfitrión
para el modo Docker.

Para el modo de desarrollo local sin Docker también se requiere:

- Python 3.12.
- PostgreSQL.
- Las dependencias de `requirements.txt`.

---

## 6. Estructura del repositorio

```text
AppSacramental/
├── AppSacramental/
│   ├── settings.py
│   ├── urls.py
│   ├── db_router.py
│   ├── asgi.py
│   └── wsgi.py
├── usuarios/
├── bautismo/
├── comunion/
├── confirmacion/
├── matrimonio/
├── agenda/
├── configuracion/
├── constancias/
├── historial/
├── reportes/
├── templates/
├── static/
├── media/                         # ignorado por Git
├── backups/                       # ignorado por Git
├── docker/
│   ├── entrypoint.sh
│   ├── gunicorn.conf.py
│   ├── nginx/
│   │   └── nginx.conf
│   └── postgres/
│       └── init/
│           ├── 01-create-databases.sh
│           └── 02-restore-dump.sh
├── scripts/
│   ├── importar_datos_locales.sh
│   └── respaldar_postgres.sh
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── requirements.txt
├── manage.py
└── README.md
```

Archivos importantes:

- `AppSacramental/settings.py`: configuración por variables de entorno.
- `AppSacramental/db_router.py`: enrutamiento de agenda e historial.
- `docker-compose.yml`: servicios, volúmenes y redes.
- `docker/entrypoint.sh`: espera de PostgreSQL, migraciones, estáticos y arranque.
- `docker/nginx/nginx.conf`: proxy inverso y archivos estáticos/media.
- `scripts/importar_datos_locales.sh`: copia SQLite y media locales a Docker.
- `scripts/respaldar_postgres.sh`: genera respaldos de PostgreSQL.

`db.sqlite3` es un archivo legado de la primera fase. La aplicación actual usa
PostgreSQL para los datos principales y las dos bases SQLite separadas para
agenda e historial.

---

## 7. Servicios Docker

| Servicio | Imagen | Función | Puerto |
| --- | --- | --- | --- |
| `db` | `postgres:18-alpine` | Base de datos principal | Interno `5432` |
| `web` | Construida con `Dockerfile` | Django + Gunicorn | Interno `8000` |
| `nginx` | `nginx:1.29-alpine` | Proxy inverso, estáticos y media | `${HTTP_PORT}:80` |

Detalles:

- `db` no publica su puerto al equipo anfitrión.
- `web` no publica su puerto; solo Nginx puede acceder a Gunicorn.
- `nginx` publica el puerto indicado por `HTTP_PORT` (por defecto `80`).
- Los servicios usan `restart: unless-stopped`.
- `web` usa `init: true` para manejar correctamente las señales del contenedor.
- Nginx usa el resolver interno `127.0.0.11` y una variable de destino para
  tolerar el cambio de IP del contenedor `web`.

Comandos útiles:

```bash
docker compose ps
docker compose logs -f
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx
```

---

## 8. Volúmenes y persistencia

| Volumen | Punto de montaje | Contenido |
| --- | --- | --- |
| `postgres_data` | `/var/lib/postgresql` | Datos de PostgreSQL 18 |
| `static_data` | `/app/staticfiles` | Archivos estáticos recolectados |
| `media_data` | `/app/media` | PDFs y archivos multimedia |
| `sqlite_data` | `/data` | `agenda.sqlite3` e `historial.sqlite3` |

Los volúmenes conservan la información aunque los contenedores se detengan o se
recrearen.

> **Importante:** `docker compose down` detiene y elimina los contenedores, pero
> conserva los volúmenes. `docker compose down -v` **elimina los volúmenes y los
> datos**. No use `down -v` salvo que tenga un respaldo verificado y sea
> realmente necesario.

PostgreSQL 18 utiliza el punto de montaje `/var/lib/postgresql`. No cambie el
volumen a `/var/lib/postgresql/data`, porque la imagen 18 lo rechaza.

---

## 9. Bases de datos y enrutamiento

### PostgreSQL principal

Base: `SACRANET_BD`.

Tablas principales del respaldo restaurado:

- `bautizos`
- `primera_comunion`
- `confirmaciones`
- `matrimonios`
- `constancias`
- `usuarios`
- `roles`
- `permisos`
- `roles_permisos`
- Tablas de Django: `auth_*`, `django_admin_log`, `django_content_type`,
  `django_migrations`, `django_session`.

### SQLite para agenda

- Alias de Django: `agenda`.
- Archivo dentro de Docker: `/data/agenda.sqlite3`.
- Aplicación enrutada: `agenda`.
- Datos actuales importados: 5 actividades.

### SQLite para historial

- Alias de Django: `historial`.
- Archivo dentro de Docker: `/data/historial.sqlite3`.
- Aplicación enrutada: `historial`.
- Datos actuales importados: 171 constancias emitidas.

### Enrutamiento

`AppSacramental/db_router.py` contiene `AgendaRouter`:

- Las consultas de `agenda` van al alias `agenda`.
- Las consultas de `historial` van al alias `historial`.
- Las demás aplicaciones usan `default` (PostgreSQL).
- `allow_migrate` impide crear tablas de otras aplicaciones en las bases
  secundarias.

Django puede registrar todas las migraciones en el historial de cada base, pero
el router evita crear las tablas que no corresponden. Por eso
`django_migrations` puede tener más entradas que tablas reales en
`agenda.sqlite3` o `historial.sqlite3`. Es el comportamiento esperado.

### Modo PostgreSQL opcional para agenda e historial

Por compatibilidad, agenda e historial usan SQLite por defecto. Si se desea
usar PostgreSQL para ambas, configure en `.env`:

```env
AGENDA_DB_ENGINE=postgresql
HISTORIAL_DB_ENGINE=postgresql
AGENDA_DB_NAME=agenda
HISTORIAL_DB_NAME=historial
```

El script `docker/postgres/init/01-create-databases.sh` crea las bases `agenda`
y `historial` cuando el volumen de PostgreSQL se inicializa por primera vez.

Si el volumen ya existe, las bases adicionales deben crearse manualmente:

```bash
docker compose exec db psql -U sacranet -d postgres -c "CREATE DATABASE agenda;"
docker compose exec db psql -U sacranet -d postgres -c "CREATE DATABASE historial;"
```

Los modelos de varias aplicaciones usan `managed = False`. No ejecute
`makemigrations` sobre ellos sin coordinar antes los cambios con la estructura
real de la base de datos.

---

## 10. Variables de entorno

El archivo `.env` no se versiona. La plantilla es `.env.example`.

| Variable | Uso | Valor recomendado |
| --- | --- | --- |
| `DEBUG` | Modo depuración de Django | `False` en Docker |
| `SECRET_KEY` | Clave secreta de Django | Cadena larga y aleatoria |
| `ALLOWED_HOSTS` | Hosts permitidos | `*` en local/LAN; dominios reales en producción |
| `CSRF_TRUSTED_ORIGINS` | Orígenes permitidos para CSRF | `http://localhost,http://127.0.0.1` y la IP LAN |
| `POSTGRES_DB` | Base principal | `SACRANET_BD` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `sacranet` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | Contraseña larga y aleatoria |
| `DB_HOST` | Host de PostgreSQL | `db` dentro de Docker |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_NAME` | Nombre de base principal | `SACRANET_BD` |
| `DB_USER` | Usuario de base principal | `sacranet` |
| `DB_PASSWORD` | Contraseña de base principal | Igual a `POSTGRES_PASSWORD` |
| `AGENDA_DB_ENGINE` | Motor de agenda | `sqlite3` o `postgresql` |
| `HISTORIAL_DB_ENGINE` | Motor de historial | `sqlite3` o `postgresql` |
| `AGENDA_DB_NAME` | Nombre/ruta de agenda | Opcional |
| `HISTORIAL_DB_NAME` | Nombre/ruta de historial | Opcional |
| `DATA_DIR` | Directorio de SQLite | `/data` en Docker |
| `DB_CONN_MAX_AGE` | Reutilización de conexiones | `60` |
| `HTTP_PORT` | Puerto publicado por Nginx | `80` |
| `GUNICORN_WORKERS` | Workers de Gunicorn | `3` |
| `GUNICORN_TIMEOUT` | Timeout de Gunicorn | `120` |
| `GUNICORN_LOG_LEVEL` | Nivel de logs | `info` |
| `RUN_MIGRATIONS` | Ejecutar migraciones al iniciar | `1` |
| `RUN_COLLECTSTATIC` | Ejecutar `collectstatic` al iniciar | `1` |
| `USE_X_FORWARDED_PROTO` | Confiar en HTTPS del proxy | Solo con HTTPS |
| `SESSION_COOKIE_SECURE` | Cookie de sesión solo HTTPS | `True` con HTTPS |
| `CSRF_COOKIE_SECURE` | Cookie CSRF solo HTTPS | `True` con HTTPS |

Para acceder desde otra computadora de la red local, agregue la IP del equipo
servidor en `ALLOWED_HOSTS` y en `CSRF_TRUSTED_ORIGINS`. Ejemplo:

```env
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.50
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://192.168.1.50
```

---

## 11. Preparación inicial del `.env`

Si el archivo `.env` no existe:

```bash
cp .env.example .env
chmod 600 .env
```

Genere valores nuevos:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
python3 -c "import secrets; print(secrets.token_hex(24))"
```

Use el primer valor para `SECRET_KEY` y el segundo para
`POSTGRES_PASSWORD`.

En el entorno de desarrollo actual ya existe un `.env` local generado con
valores aleatorios. Ese archivo está ignorado por Git y no debe compartirse.

No use las contraseñas de ejemplo de `.env.example` en un entorno real.

---

## 12. Construcción y arranque

Desde la carpeta que contiene `docker-compose.yml`:

```bash
docker compose build
docker compose up -d
```

Verificar el estado:

```bash
docker compose ps
```

Esperar a que `db`, `web` y `nginx` aparezcan como `healthy`.

Ver logs:

```bash
docker compose logs -f web
```

Abrir en el navegador:

```text
http://localhost/
```

O desde otro equipo de la red:

```text
http://IP_DEL_EQUIPO/
```

Si el puerto 80 está ocupado, cambie `HTTP_PORT` en `.env`:

```env
HTTP_PORT=8080
```

Luego:

```bash
docker compose up -d nginx
```

La aplicación quedará en `http://localhost:8080/`.

---

## 13. Carga inicial de datos

El respaldo principal recomendado es:

```text
backups/SACRANET_BD.dump
```

Para que se restaure automáticamente en un volumen nuevo, cópielo antes del
primer arranque:

```bash
cp backups/SACRANET_BD.dump docker/postgres/init/SACRANET_BD.dump
docker compose up -d
```

El script `docker/postgres/init/02-restore-dump.sh` detecta automáticamente:

- `SACRANET_BD.dump`
- `SACRANET_BD.backup`
- `SACRANET_BD.sql`
- `Sacranet_BD.sql`

Los scripts de inicialización solo se ejecutan cuando el volumen de PostgreSQL
está vacío. Si el volumen ya existe, no se vuelven a ejecutar.

`Sacranet_BD.sql` contiene solo cuatro tablas sacramentales y no es el respaldo
principal. Use preferentemente `SACRANET_BD.dump`.

No restaure un respaldo sobre una base que ya está en uso sin respaldarla
primero. Para una restauración segura, use un volumen nuevo o una base temporal.

---

## 14. Importación de datos locales (SQLite y media)

Para copiar las bases SQLite y los archivos multimedia locales a los volúmenes
de Docker:

```bash
bash scripts/importar_datos_locales.sh
```

El script:

1. Pide confirmación.
2. Detiene temporalmente el contenedor `web`.
3. Copia `agenda.sqlite3` a `/data/agenda.sqlite3`.
4. Copia `historial.sqlite3` a `/data/historial.sqlite3`.
5. Copia el contenido de `media/` a `/app/media/`.
6. Ajusta los permisos de los volúmenes para `appuser`.
7. Vuelve a iniciar `web`.

Los archivos originales del equipo no se modifican. Los archivos que ya existan
en los volúmenes con el mismo nombre se reemplazan.

La base principal de PostgreSQL no se copia con este script; para esos datos use
el respaldo `backups/SACRANET_BD.dump`.

Datos importados durante las pruebas:

- Agenda: 5 actividades.
- Historial: 171 constancias emitidas.
- Multimedia: 254 archivos, aproximadamente 133 MB.

---

## 15. Migraciones y tareas de inicio

El entrypoint `docker/entrypoint.sh` realiza lo siguiente al iniciar `web`:

1. Espera a que PostgreSQL acepte conexiones.
2. Ejecuta `migrate` en la base `default`.
3. Ejecuta `migrate --database=agenda`.
4. Ejecuta `migrate --database=historial`.
5. Ejecuta `collectstatic --noinput`.
6. Inicia Gunicorn.

Para omitir tareas temporalmente:

```env
RUN_MIGRATIONS=0
RUN_COLLECTSTATIC=0
```

Comandos manuales:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py migrate --database=agenda
docker compose exec web python manage.py migrate --database=historial
docker compose exec web python manage.py collectstatic --noinput
```

Durante el arranque puede aparecer un aviso similar a:

```text
Your models in app(s): 'bautismo', 'comunion', 'configuracion',
'confirmacion', 'matrimonio', 'usuarios' have changes that are not yet
reflected in a migration
```

Es esperado porque esos modelos usan `managed = False`. No ejecute
`makemigrations` sobre ellos sin revisar la estructura real de la base.

---

## 16. Archivos estáticos y multimedia

### Estáticos

- Django ejecuta `collectstatic` al iniciar.
- Los archivos se guardan en `/app/staticfiles`.
- Nginx los sirve desde `/static/`.
- El volumen `static_data` conserva los archivos recolectados.

Prueba:

```bash
curl -I http://localhost/static/usuarios/css/login.css
```

### Multimedia

- Los PDFs y archivos subidos se guardan en `/app/media`.
- Nginx los sirve desde `/media/`.
- El volumen `media_data` conserva los archivos.
- `media/` está ignorado por Git y por la imagen Docker.

Prueba:

```bash
curl -I http://localhost/media/constancias/2026/10/ARCHIVO.pdf
```

Si un archivo estático o multimedia no aparece, revise:

```bash
docker compose logs -f nginx
docker compose exec web ls -l /app/staticfiles
docker compose exec web ls -l /app/media
```

---

## 17. Acceso a la aplicación

Direcciones principales:

| Ruta | Función |
| --- | --- |
| `/` | Panel principal |
| `/login/` | Inicio de sesión de Sacranet |
| `/admin/` | Administración de Django |
| `/bautismo/` | Módulo de bautismo |
| `/comunion/` | Módulo de primera comunión |
| `/confirmacion/` | Módulo de confirmación |
| `/matrimonio/` | Módulo de matrimonio |
| `/agenda/` | Agenda parroquial |
| `/configuracion/` | Configuración y usuarios |
| `/sacramentos/bautismo/` | Listado de bautismos |
| `/sacramentos/comunion/` | Listado de primeras comuniones |
| `/sacramentos/confirmacion/` | Listado de confirmaciones |
| `/sacramentos/matrimonio/` | Listado de matrimonios |

El inicio de sesión de Sacranet usa la tabla `usuarios`. El usuario de
`/admin/` es independiente y pertenece al sistema de autenticación de Django.

---

## 18. Inicio de sesión y roles

El inicio de sesión está en `usuarios/views.py`.

La sesión guarda:

- `usuario_id`
- `username`
- `rol_id`
- `rol_nombre`

La contraseña se valida con `check_password` contra el campo `password_hash` de
la tabla `usuarios`.

Roles existentes:

| ID | Rol |
| --- | --- |
| 1 | Administrador |
| 2 | Secretaría |
| 3 | Consulta |

La sección `configuracion` está reservada al Administrador. Las restricciones
deben validarse en el servidor y no solo ocultando opciones en la interfaz.

Crear un usuario de Sacranet desde la consola:

```bash
docker compose exec web python manage.py shell
```

```python
from usuarios.models import Usuario

usuario = Usuario(username="nuevo_usuario", id_rol_id=2)
usuario.set_password("UnaContrasenaSegura123!")
usuario.save()
```

Crear un superusuario para `/admin/`:

```bash
docker compose exec web python manage.py createsuperuser
```

No confunda el usuario de `/admin/` con los usuarios de la tabla `usuarios`.

---

## 19. Módulos funcionales

| Aplicación | Función | Estado |
| --- | --- | --- |
| `usuarios` | Inicio y cierre de sesión | Funcional |
| `bautismo` | Registros de bautismo y PDF | En pruebas |
| `comunion` | Primeras comuniones y PDF | En pruebas |
| `confirmacion` | Confirmaciones y PDF | En pruebas |
| `matrimonio` | Matrimonios y PDF | En pruebas |
| `agenda` | Actividades parroquiales | En pruebas |
| `configuracion` | Usuarios y configuración | En pruebas |
| `constancias` | Emisión de constancias | En pruebas |
| `historial` | Historial de constancias emitidas | En pruebas |
| `reportes` | Reportes y estadísticas | No registrada en `INSTALLED_APPS` |

Los módulos principales respondieron correctamente en las pruebas HTTP. La
validación funcional completa de cada rol y de la generación de constancias debe
seguir realizándose antes de considerar terminada cada función.

---

## 20. Operación y mantenimiento

### Ver logs

```bash
docker compose logs -f
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx
```

### Reiniciar servicios

```bash
docker compose restart
```

### Aplicar cambios de código

```bash
docker compose up -d --build
```

### Recrear solo `web`

```bash
docker compose up -d --force-recreate --no-deps web
```

Nginx puede devolver `502` durante los primeros segundos mientras `web` termina
de ejecutar migraciones, `collectstatic` y el arranque de Gunicorn. Espere a que
el servicio aparezca como `healthy`.

### Abrir una consola de Django

```bash
docker compose exec web python manage.py shell
```

### Abrir PostgreSQL

```bash
docker compose exec db psql -U sacranet -d SACRANET_BD
```

### Verificar configuración

```bash
docker compose exec web python manage.py check
```

### Actualizar dependencias

1. Edite `requirements.txt`.
2. Ejecute `docker compose build`.
3. Ejecute `docker compose up -d`.

---

## 21. Respaldos y restauración

### Respaldar PostgreSQL

```bash
bash scripts/respaldar_postgres.sh
```

El respaldo se guarda en:

```text
backups/SACRANET_BD_AAAAMMDD_HHMMSS.dump
```

También se puede generar manualmente:

```bash
docker compose exec -T db pg_dump -U sacranet -d SACRANET_BD --format=custom \
    > backups/SACRANET_BD_$(date +%Y%m%d_%H%M%S).dump
```

### Respaldar SQLite

```bash
docker compose cp web:/data/agenda.sqlite3 backups/agenda_$(date +%F).sqlite3
docker compose cp web:/data/historial.sqlite3 backups/historial_$(date +%F).sqlite3
```

### Respaldar multimedia

```bash
mkdir -p backups/media
docker compose cp web:/app/media/. backups/media/
```

### Restaurar PostgreSQL en una base nueva

Primero cree una base temporal:

```bash
docker compose exec db psql -U sacranet -d postgres \
    -c "CREATE DATABASE SACRANET_BD_RESTAURACION;"
```

Restaure:

```bash
docker compose exec -T db pg_restore -U sacranet -d SACRANET_BD_RESTAURACION \
    --no-owner --no-privileges --exit-on-error \
    < backups/SACRANET_BD_AAAAMMDD_HHMMSS.dump
```

Verifique y luego decida si reemplaza la base principal. No sobrescriba la base
en uso sin un respaldo previo.

### Restaurar SQLite

Detenga `web`, copie el archivo y vuelva a iniciar:

```bash
docker compose stop web
docker compose cp backups/agenda_2026-10-31.sqlite3 web:/data/agenda.sqlite3
docker compose cp backups/historial_2026-10-31.sqlite3 web:/data/historial.sqlite3
docker compose start web
```

Ajuste los permisos si es necesario:

```bash
docker compose run --rm --no-deps -u root --entrypoint sh web \
    -c 'chown -R appuser:appuser /data /app/media'
```

---

## 22. Solución de problemas

| Problema | Causa probable | Solución |
| --- | --- | --- |
| `db` reiniciándose | Volumen montado en ruta incorrecta de PostgreSQL 18 | Use `postgres_data:/var/lib/postgresql` |
| Error sobre datos en `/var/lib/postgresql/data` | Volumen creado con la ruta antigua | Respalde y cree un volumen nuevo; no borre datos sin respaldo |
| `502 Bad Gateway` | `web` aún no está listo | Espere a `healthy` y revise `docker compose logs -f web` |
| `400 Bad Request` | Host no permitido | Agregue la IP/dominio a `ALLOWED_HOSTS` |
| `403 CSRF` desde la LAN | Origen no confiable | Agregue `http://IP` a `CSRF_TRUSTED_ORIGINS` |
| No se puede iniciar sesión | Usuario inexistente, contraseña incorrecta o problema de conexión | Revise `usuarios`, cree un usuario temporal y verifique los logs |
| Estáticos en 404 | `collectstatic` no ejecutado o volumen vacío | Ejecute `collectstatic` y revise Nginx |
| Media en 404 | Archivos no importados | Ejecute `scripts/importar_datos_locales.sh` |
| Puerto 80 ocupado | Otro servicio usa el puerto | Cambie `HTTP_PORT` en `.env` |
| `.env` no encontrado | No se creó el archivo | `cp .env.example .env` y configure valores |
| Permiso denegado en SQLite | Propietario incorrecto en el volumen | Ejecute el `chown` mostrado en la sección de respaldos |
| `makemigrations` sugiere cambios | Modelos con `managed = False` | No generar migraciones sin revisar la base real |

Comandos de diagnóstico:

```bash
docker compose ps
docker compose config
docker compose logs --tail=100 web
docker compose exec web python manage.py check
docker compose exec web python manage.py showmigrations
```

---

## 23. Seguridad y HTTPS

La configuración actual está preparada para HTTP en local o red interna.

Medidas ya aplicadas:

- `DEBUG=False` en el `.env` de Docker.
- `SECRET_KEY` y contraseña de PostgreSQL generadas aleatoriamente.
- PostgreSQL no publica su puerto al exterior.
- Gunicorn no publica su puerto al exterior.
- Nginx agrega cabeceras `X-Content-Type-Options`, `X-Frame-Options` y
  `Referrer-Policy`.
- El contenedor `web` se ejecuta como usuario no root.
- `.env`, respaldos, SQLite y media están ignorados por Git.

Antes de publicar en Internet:

1. Restrinja `ALLOWED_HOSTS` a los dominios reales.
2. Configure `CSRF_TRUSTED_ORIGINS` con los orígenes HTTPS exactos.
3. Instale un certificado TLS y configure el bloque HTTPS de Nginx.
4. Active:

```env
USE_X_FORWARDED_PROTO=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

5. Configure un backend de correo real si se usará recuperación de contraseña.
   Actualmente `MAILERS` usa el backend de consola.
6. Realice respaldos automáticos y pruebe la restauración.
7. Ejecute `python manage.py check --deploy` y revise los avisos.

`ALLOWED_HOSTS=*` es aceptable para pruebas locales o LAN, pero no para
producción.

---

## 24. Pruebas realizadas y checklist final

### Pruebas ejecutadas

- [x] `docker compose build` sin errores.
- [x] `docker compose up -d` con `db`, `web` y `nginx` saludables.
- [x] Restauración de `backups/SACRANET_BD.dump` con `--exit-on-error`.
- [x] PostgreSQL con 403 bautizos y 2 usuarios después de la restauración.
- [x] Importación de `agenda.sqlite3` con 5 actividades.
- [x] Importación de `historial.sqlite3` con 171 registros.
- [x] Archivos multimedia importados y servidos por Nginx.
- [x] Inicio de sesión probado con usuario temporal; usuario eliminado después.
- [x] Acceso HTTP a los módulos principales con respuesta `200`.
- [x] Archivos estáticos servidos con respuesta `200`.
- [x] Archivos PDF servidos con respuesta `200`.
- [x] Persistencia comprobada después de `docker compose down` y `up`.
- [x] Aplicación disponible en el puerto 80.
- [x] `manage.py check` sin errores.

### Pendientes recomendados

- [ ] Probar inicio de sesión y permisos con cada rol real.
- [ ] Probar la emisión completa de una constancia y su registro en historial.
- [ ] Verificar las estadísticas del panel con datos reales.
- [ ] Configurar HTTPS si se publicará fuera de la red local.
- [ ] Configurar SMTP si se usará correo.
- [ ] Programar respaldos automáticos.
- [ ] Revisar `python manage.py check --deploy` antes de producción.

### Comandos de verificación rápida

```bash
docker compose ps
curl -I http://localhost/
curl -I http://localhost/login/
curl -I http://localhost/static/usuarios/css/login.css
docker compose exec web python manage.py check
docker compose logs --tail=50 web
```
