
Sacranet --- Gestión de registros sacramentales

Sacranet es una aplicación web desarrollada para apoyar las tareas
administrativas de una parroquia. Permite trabajar con registros
sacramentales, administrar el acceso de los usuarios, organizar
actividades y consultar información desde un panel principal.

El proyecto se desarrolla con Django y Python. La información se
distribuye entre PostgreSQL y SQLite según el tipo de dato, para
mantener separadas las funciones de cada base de datos.
Estado del proyecto

Última actualización: 13 de octubre de 2026
Estado: en desarrollo

Este documento describe el avance actual. Algunas funciones siguen en
ajuste y no se consideran terminadas hasta completar sus pruebas.
Tecnologías utilizadas

    Python 3.12.3
    Django 6.1
    PostgreSQL para los datos sacramentales y la información
    principal de usuarios, roles y permisos.
    SQLite para la agenda y el historial de constancias emitidas.
    HTML y CSS para las páginas y los componentes de la interfaz.
    Git y GitHub para el control de versiones.

Organización de la aplicación

El proyecto está dividido en aplicaciones Django, cada una enfocada en
una parte del trabajo:

Aplicación Función

usuarios Inicio de sesión y manejo de la
sesión del usuario.

configuracion Área de administración de usuarios
y configuración de acceso.

reportes Consultas y presentación de
información para reportes y
estadísticas.

agenda Registro y consulta de actividades.

bautismo Funciones relacionadas con los
registros de bautismo.

comunion Funciones relacionadas con los
registros de primera comunión.

confirmacion Funciones relacionadas con los
registros de confirmación.

matrimonio Funciones relacionadas con los
registros de matrimonio.

constancias Funciones relacionadas con la
emisión de constancias.

La configuración general de Django se encuentra en el paquete
AppSacramental, junto con settings.py, urls.py, asgi.py y
wsgi.py. El archivo manage.py se utiliza para ejecutar las tareas
administrativas del proyecto.
Bases de datos

Sacranet utiliza bases de datos separadas para evitar mezclar
información de distinta naturaleza.
PostgreSQL: AppSacramental

Es la base de datos principal. Contiene los registros sacramentales y
las tablas relacionadas con usuarios, roles y permisos. Entre las tablas
existentes se encuentran:

    bautismos
    primeras_comuniones
    confirmaciones
    matrimonios
    usuarios
    roles
    permisos
    roles_permisos

La estructura existente se conserva en PostgreSQL; la información
sacramental no se traslada a las bases SQLite.
SQLite: agenda

La agenda utiliza el archivo agenda.sqlite3. Su acceso se dirige
mediante AgendaRouter, que permite enviar las operaciones de la
aplicación agenda a esta base de datos y mantener las demás
aplicaciones en PostgreSQL.
SQLite: historial de constancias

El historial de emisiones se almacena en historial.sqlite3. La idea es
registrar cada constancia emitida con información como:

    Nombre asociado al registro.
    Sacramento.
    Usuario que realizó la emisión.
    Fecha y hora de emisión.

El historial se está conectando con las funciones de emisión y con las
estadísticas del panel principal. Las constancias de prueba que ya
estaban en PostgreSQL no se importan automáticamente al historial: este
se alimenta con nuevas emisiones registradas desde la aplicación.
Acceso y roles

El inicio de sesión está en usuarios. La sesión conserva datos del
usuario autenticado, incluido su identificador, nombre y rol. La
validación de contraseñas utiliza check_password sobre el campo
password_hash del modelo existente.

Los roles contemplados en la base de datos son:

    Administrador
    Secretaría
    Consulta

La sección configuracion está reservada al Administrador. Los
usuarios con los roles Secretaría y Consulta no deben poder
crear usuarios ni cambiar contraseñas. Estas restricciones deben
comprobarse en las vistas y en el servidor, no solamente ocultando
opciones en la interfaz.
Funciones desarrolladas y en proceso
Inicio de sesión

    Se conserva el inicio de sesión existente en la aplicación
    usuarios.
    Se utilizan datos de sesión para identificar al usuario y su rol.
    La navegación debe respetar los permisos correspondientes al rol
    autenticado.

Registros sacramentales y constancias

    La aplicación cuenta con secciones para bautismo, primera comunión,
    confirmación y matrimonio.
    Se trabaja con la base PostgreSQL que contiene los registros.
    La emisión de constancias de primera comunión y confirmación ya
    incluye una llamada para guardar el evento en el historial SQLite
    después de generar el PDF.
    La conexión del historial con todas las emisiones y las gráficas
    debe verificarse con pruebas por sacramento.

Agenda

    La agenda utiliza su propia base SQLite.
    El enrutamiento de base de datos se realiza con AgendaRouter.
    La carga de actividades, el registro de nuevas actividades y los
    contadores del panel requieren validación de extremo a extremo.
    Durante el desarrollo se detectó un problema de resolución de URL
    relacionado con el nombre agenda_crear; debe comprobarse que la
    ruta exista y coincida con la que utiliza la plantilla.

Panel principal y estadísticas

    Se trabaja en un panel con indicadores y gráficas.
    Las estadísticas de emisiones deben basarse en los registros reales
    del historial, no en valores escritos manualmente.
    Para comprobar el flujo, se debe emitir una constancia, confirmar
    que aparece en historial.sqlite3 y verificar que el panel refleje
    el nuevo registro.

Administración de usuarios

    La sección de configuración se está preparando para la
    administración de usuarios.
    El acceso a esta sección debe quedar limitado al Administrador.
    La creación de usuarios y el cambio de contraseñas deben contar con
    validación del lado del servidor antes de considerarse terminados.

Requisitos para desarrollo

Se necesita tener instalados Python 3.12, Django 6.1 y PostgreSQL,
además de las dependencias definidas para el proyecto. SQLite está
incluido con Python y no requiere instalar un servidor separado.

Los comandos siguientes se ejecutan desde la carpeta que contiene
manage.py.
Preparar el entorno

En Ubuntu, se puede crear y activar un entorno virtual con:
python3 -m venv venv
source venv/bin/activate

Instalar las dependencias:
pip install -r requirements.txt

Este último comando requiere que el archivo requirements.txt esté
presente y actualizado en el repositorio. Si todavía no existe, hay que
instalar las dependencias del proyecto y generar el archivo antes de
usar este paso.
Configurar las bases de datos

Antes de iniciar la aplicación, configurar el acceso a PostgreSQL en
AppSacramental/settings.py o en las variables de entorno que utilice
el proyecto. Revisar que estén definidas las conexiones para la base
principal y las bases SQLite de agenda e historial.

No se deben cambiar las bases de datos de la aplicación sin revisar
también DATABASES, DATABASE_ROUTERS y las migraciones
correspondientes.
Comprobar la configuración
python manage.py check
Aplicar migraciones
python manage.py migrate

Las migraciones deben ejecutarse respetando la configuración de
enrutamiento. Si se necesitan migraciones específicas para una base,
revisar el router y utilizar el alias correcto antes de ejecutar
comandos adicionales.
Iniciar el servidor de desarrollo
python manage.py runserver

Por defecto, Django publica el servidor local en
http://127.0.0.1:8000/. Este servidor es para desarrollo; no debe
exponerse directamente a Internet como despliegue de producción.
Estructura general

La estructura puede variar conforme avance el desarrollo, pero la
organización principal es similar a la siguiente:
AppSacramental/
├── manage.py
├── AppSacramental/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── usuarios/
├── configuracion/
├── reportes/
├── agenda/
├── bautismo/
├── comunion/
├── confirmacion/
├── matrimonio/
├── constancias/
├── agenda.sqlite3
└── historial.sqlite3

Los archivos SQLite se muestran como referencia de su ubicación
conocida; su ruta definitiva depende de la configuración del proyecto.
PostgreSQL se ejecuta como servicio independiente, por lo que no aparece
como archivo dentro de esta estructura.
Pruebas recomendadas antes de dar una función por terminada

    Iniciar sesión con cada rol y comprobar qué secciones puede abrir.
    Confirmar que Secretaría y Consulta no pueden acceder a las
    funciones de creación de usuarios o cambio de contraseñas, incluso
    si intentan abrir las URL directamente.
    Registrar y consultar una actividad de agenda; verificar que se
    guarde en SQLite.
    Emitir una constancia y confirmar que el PDF se genere
    correctamente.
    Revisar en historial.sqlite3 que la emisión guarde el nombre, el
    sacramento, el usuario y la fecha.
    Confirmar que las estadísticas del panel cambien a partir de los
    datos guardados.
    Probar los formularios con datos válidos, campos vacíos y registros
    inexistentes.
    Ejecutar python manage.py check después de cambios en modelos,
    rutas o configuración.

Consideraciones

    Mantener separados PostgreSQL, la base SQLite de agenda y la base
    SQLite de historial.
    No eliminar ni recrear las tablas existentes de PostgreSQL para
    resolver problemas de la interfaz.
    No considerar una función terminada solo porque la página cargue;
    también hay que probar las operaciones y los permisos en el
    servidor.
    Evitar guardar contraseñas en texto plano.
    Antes de modificar datos reales, realizar una copia de seguridad de
    las bases correspondientes.
    El servidor de desarrollo de Django no sustituye una configuración
    de producción.

Próximos pasos

    Terminar de validar las rutas y operaciones de la agenda.
    Completar la administración de usuarios desde configuracion,
    manteniendo el acceso exclusivo del Administrador.
    Verificar el registro de emisiones en el historial para todos los
    sacramentos que generan constancias.
    Conectar y validar las gráficas del panel con los datos reales.
    Realizar pruebas funcionales de los flujos principales y documentar
    cualquier cambio de configuración necesario para instalar el
    proyecto en otro equipo.

Sacranet
Proyecto académico de desarrollo web para la gestión de registros
sacramentales.