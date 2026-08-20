Sistema de Gestión Sacramental – Iglesia El Calvario

Fase 1 — Configuración inicial y arquitectura base

1. Descripción del proyecto

El proyecto Sistema de Gestión Sacramental – Iglesia El Calvario tiene como propósito centralizar la administración de los registros sacramentales de la iglesia mediante una aplicación web.

De acuerdo con el Acta de Constitución del Proyecto, el sistema contempla la gestión de feligreses, registros de Bautismo, Primera Comunión, Confirmación y Matrimonio, generación de constancias, reportes, control de acceso, auditoría y respaldos.

Nota: El Acta de Constitución actualmente indica PHP con Laravel como tecnología de implementación. La implementación realizada en esta fase utiliza Django/Python. Esta diferencia deberá ser actualizada o formalmente justificada en la documentación del proyecto.

2. Objetivo de la Fase 1

Establecer la estructura inicial del proyecto web utilizando Django, dejando preparada la arquitectura base para el desarrollo progresivo de los módulos funcionales del sistema.

En esta fase se realizó:

Creación del proyecto Django.

Configuración del entorno virtual.

Configuración inicial de la aplicación principal.

Creación de las aplicaciones Django principales.

Registro de las aplicaciones en INSTALLED_APPS.

Configuración y ejecución de las migraciones iniciales.

Configuración inicial de directorios para templates, archivos estáticos y archivos multimedia.

Verificación del funcionamiento del proyecto mediante check y runserver.

3. Tecnologías utilizadas

Backend

Python

Django

Base de datos inicial

SQLite

Frontend

La estructura queda preparada para incorporar posteriormente la interfaz web y los recursos estáticos del sistema.

Entorno

Entorno virtual de Python (venv)

4. Estructura actual del proyecto

La estructura base establecida durante esta fase es:

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

5. Aplicaciones Django

Se crearon las siguientes aplicaciones para separar las responsabilidades principales del sistema:

Aplicación

Propósito

usuarios

Gestión de usuarios y control de acceso.

feligreses

Administración de la información de los feligreses.

sacramentos

Gestión de los registros sacramentales.

constancias

Gestión de la generación de constancias.

reportes

Generación y gestión de reportes.

auditoria

Registro de operaciones críticas y trazabilidad.

Estas aplicaciones representan la división inicial de responsabilidades del sistema. La lógica detallada y los modelos de datos serán desarrollados en fases posteriores.

6. Directorios globales

Se establecieron los siguientes directorios:

templates/

Contendrá las plantillas HTML generales del sistema.

static/

Contendrá archivos estáticos como:

CSS

JavaScript

Imágenes

Otros recursos estáticos

media/

Se utilizará para archivos generados o cargados por el sistema que correspondan a contenido multimedia o documentos.

7. Configuración realizada

Templates

Se configuró Django para buscar plantillas en:

BASE_DIR / 'templates'

Archivos estáticos

Se configuró:

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

Archivos multimedia

Se configuró:

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

8. Base de datos

Durante esta fase se mantiene SQLite como base de datos inicial del proyecto.

El archivo generado actualmente es:

db.sqlite3

Las migraciones iniciales de Django fueron ejecutadas correctamente mediante:

python manage.py migrate

La decisión definitiva sobre el motor de base de datos para el entorno de producción será documentada posteriormente.

9. Verificaciones realizadas

Se realizaron las siguientes comprobaciones:

Verificación de configuración

python manage.py check

Resultado esperado:

System check identified no issues (0 silenced).

Migraciones

python manage.py migrate

Servidor de desarrollo

python manage.py runserver

El proyecto fue comprobado mediante el servidor de desarrollo de Django.

10. Problema encontrado y solución

Durante la configuración de la aplicación sacramentos se produjo un error debido a una diferencia entre el nombre de la aplicación y el valor definido en apps.py.

El error indicaba:

ModuleNotFoundError: No module named 'sacramento'

La configuración fue corregida para utilizar el nombre correcto:

class SacramentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sacramentos'

Después de la corrección, las comprobaciones y migraciones pudieron ejecutarse correctamente.

11. Estado de la Fase 1

Estado: Completada

La estructura inicial del proyecto Django se encuentra funcionando y preparada para comenzar el desarrollo de los módulos funcionales.

Completado

Proyecto Django creado.

Entorno virtual configurado.

Base de datos SQLite inicial.

Aplicaciones principales creadas.

Aplicaciones registradas en Django.

Migraciones iniciales ejecutadas.

Directorio templates/ creado.

Directorio static/ creado.

Directorio media/ creado.

Configuración inicial de templates.

Configuración inicial de archivos estáticos.

Configuración inicial de archivos multimedia.

Verificación del proyecto mediante manage.py check.

Ejecución del servidor de desarrollo.

12. Próxima fase

La siguiente fase deberá continuar con la configuración y diseño de la aplicación, incluyendo la estructura de navegación, interfaz base, configuración de URLs y posteriormente el diseño de los modelos de datos necesarios para representar feligreses y registros sacramentales.

13. Referencia del proyecto

Proyecto: Sistema de Gestión Sacramental – Iglesia El Calvario

Patrocinador: Párroco de la Iglesia El Calvario

Fecha del Acta de Constitución: 17/08/2026

Estado del Acta: Pendiente de aprobación