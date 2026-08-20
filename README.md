# Sistema de Gestión Sacramental – Iglesia El Calvario

## Fase 1 — Configuración inicial y arquitectura base

### Descripción del proyecto

El proyecto **Sistema de Gestión Sacramental – Iglesia El Calvario** tiene como propósito centralizar la administración de los registros sacramentales de la iglesia mediante una aplicación web.

De acuerdo con el **Acta de Constitución del Proyecto**, el sistema contempla:

* Gestión de feligreses.
* Registros de Bautismo.
* Registros de Primera Comunión.
* Registros de Confirmación.
* Registros de Matrimonio.
* Generación de constancias.
* Generación de reportes.
* Control de acceso.
* Auditoría.
* Respaldos.

> **Nota:** El Acta de Constitución actualmente indica **PHP con Laravel** como tecnología de implementación. La implementación realizada en esta fase utiliza **Django/Python**. Esta diferencia deberá ser actualizada o formalmente justificada en la documentación del proyecto.

---

## Objetivo de la Fase 1

Establecer la estructura inicial del proyecto web utilizando **Django**, dejando preparada la arquitectura base para el desarrollo progresivo de los módulos funcionales del sistema.

En esta fase se realizó:

* Creación del proyecto Django.
* Configuración del entorno virtual.
* Configuración inicial de la aplicación principal.
* Creación de las aplicaciones Django principales.
* Registro de las aplicaciones en `INSTALLED_APPS`.
* Configuración y ejecución de las migraciones iniciales.
* Configuración inicial de directorios para templates, archivos estáticos y archivos multimedia.
* Verificación del funcionamiento del proyecto mediante `check` y `runserver`.

---

## Tecnologías utilizadas

### Backend

* Python
* Django

### Base de datos inicial

* SQLite

### Frontend

La estructura queda preparada para incorporar posteriormente la interfaz web y los recursos estáticos del sistema.

### Entorno

* Entorno virtual de Python (`venv`)

---

## Estructura actual del proyecto

La estructura base establecida durante esta fase es:

```text
AppSacramental/
├── venv/
├── db.sqlite3
├── manage.py
│
├── Appsacramental/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __pycache__/
│
├── usuarios/
├── feligreses/
├── sacramentos/
├── constancias/
├── reportes/
├── auditoria/
│
├── templates/
├── static/
└── media/
```

---

## Aplicaciones Django

Se crearon las siguientes aplicaciones para separar las responsabilidades principales del sistema:

| Aplicación    | Propósito                                           |
| ------------- | --------------------------------------------------- |
| `usuarios`    | Gestión de usuarios y control de acceso.            |
| `feligreses`  | Administración de la información de los feligreses. |
| `sacramentos` | Gestión de los registros sacramentales.             |
| `constancias` | Gestión de la generación de constancias.            |
| `reportes`    | Generación y gestión de reportes.                   |
| `auditoria`   | Registro de operaciones críticas y trazabilidad.    |

Estas aplicaciones representan la división inicial de responsabilidades del sistema. La lógica detallada y los modelos de datos serán desarrollados en fases posteriores.

---

## Directorios globales

Se establecieron los siguientes directorios:

### `templates/`

Contendrá las plantillas HTML generales del sistema.

### `static/`

Contendrá archivos estáticos como:

* CSS.
* JavaScript.
* Imágenes.
* Otros recursos estáticos.

### `media/`

Se utilizará para archivos generados o cargados por el sistema que correspondan a contenido multimedia o documentos.

---

## Configuración realizada

### Templates

Se configuró Django para buscar plantillas en:

```python
BASE_DIR / 'templates'
```

### Archivos estáticos

Se configuró:

```python
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### Archivos multimedia

Se configuró:

```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## Base de datos

Durante esta fase se mantiene **SQLite** como base de datos inicial del proyecto.

El archivo generado actualmente es:

```text
db.sqlite3
```

Las migraciones iniciales de Django fueron ejecutadas correctamente mediante:

```bash
python manage.py migrate
```

La decisión definitiva sobre el motor de base de datos para el entorno de producción será documentada posteriormente.

---

## Verificaciones realizadas

Se realizaron las siguientes comprobaciones.

### Verificación de configuración

```bash
python manage.py check
```

**Resultado esperado:**

```text
System check identified no issues (0 silenced).
```

### Migraciones

```bash
python manage.py migrate
```

### Servidor de desarrollo

```bash
python manage.py runserver
```

El proyecto fue comprobado mediante el servidor de desarrollo de Django.

---

## Problema encontrado y solución

Durante la configuración de la aplicación `sacramentos` se produjo un error debido a una diferencia entre el nombre de la aplicación y el valor definido en `apps.py`.

El error indicaba:

```text
ModuleNotFoundError: No module named 'sacramento'
```

La configuración fue corregida para utilizar el nombre correcto:

```python
class SacramentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sacramentos'
```

Después de la corrección, las comprobaciones y migraciones pudieron ejecutarse correctamente.

---

## Estado de la Fase 1

**Estado: Completada**

La estructura inicial del proyecto Django se encuentra funcionando y preparada para comenzar el desarrollo de los módulos funcionales.

### Completado

* [x] Proyecto Django creado.
* [x] Entorno virtual configurado.
* [x] Base de datos SQLite inicial.
* [x] Aplicaciones principales creadas.
* [x] Aplicaciones registradas en Django.
* [x] Migraciones iniciales ejecutadas.
* [x] Directorio `templates/` creado.
* [x] Directorio `static/` creado.
* [x] Directorio `media/` creado.
* [x] Configuración inicial de templates.
* [x] Configuración inicial de archivos estáticos.
* [x] Configuración inicial de archivos multimedia.
* [x] Verificación del proyecto mediante `manage.py check`.
* [x] Ejecución del servidor de desarrollo.

---

## Próxima fase

La siguiente fase deberá continuar con la configuración y diseño de la aplicación, incluyendo:

1. Estructura de navegación.
2. Interfaz base.
3. Configuración de URLs.
4. Diseño de los modelos de datos.
5. Representación de los feligreses.
6. Representación de los registros sacramentales.

---

## Referencia del proyecto

| Elemento                           | Información                                          |
| ---------------------------------- | ---------------------------------------------------- |
| **Proyecto**                       | Sistema de Gestión Sacramental – Iglesia El Calvario |
| **Patrocinador**                   | Párroco de la Iglesia El Calvario                    |
| **Fecha del Acta de Constitución** | 17/08/2026                                           |
| **Estado del Acta**                | Pendiente de aprobación                              |
