import os
import tempfile

from types import SimpleNamespace
from unittest.mock import patch

from pathlib import Path

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from . import servicios
from .views import administrador_requerido


class RetencionRespaldosTests(SimpleTestCase):

    def test_conserva_las_copias_mas_recientes(self):
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)

            nombres = []

            for indice in range(4):
                nombre = (
                    f'sacranet_manual_2026010{indice}_'
                    f'120000_abcdef.dump'
                )
                ruta = directorio / nombre
                ruta.write_bytes(b'respaldo')
                os.utime(
                    ruta,
                    (1000 + indice, 1000 + indice),
                )
                nombres.append(nombre)

            with override_settings(
                BACKUP_DIR=directorio,
                BACKUP_RETENTION=2,
            ):
                eliminados = servicios.aplicar_retencion()

            restantes = sorted(
                ruta.name
                for ruta in directorio.glob('*.dump')
            )

            self.assertEqual(len(eliminados), 2)
            self.assertEqual(
                restantes,
                sorted(nombres[-2:]),
            )

    def test_retencion_cero_no_elimina_respaldos(self):
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)

            for indice in range(3):
                ruta = directorio / (
                    f'sacranet_manual_2026010{indice}_'
                    f'120000_abcdef.dump'
                )
                ruta.write_bytes(b'respaldo')

            with override_settings(
                BACKUP_DIR=directorio,
                BACKUP_RETENTION=0,
            ):
                eliminados = servicios.aplicar_retencion()

            self.assertEqual(eliminados, [])
            self.assertEqual(
                len(list(directorio.glob('*.dump'))),
                3,
            )


class SeguridadRespaldosTests(SimpleTestCase):

    def test_rechaza_nombres_con_ruta(self):
        with tempfile.TemporaryDirectory() as temporal:
            with override_settings(BACKUP_DIR=Path(temporal)):
                with self.assertRaises(servicios.ErrorRespaldo):
                    servicios.validar_ruta('../intruso.dump')

                with self.assertRaises(servicios.ErrorRespaldo):
                    servicios.validar_ruta('archivo.txt')

    def test_acepta_nombre_valido_dentro_del_directorio(self):
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal).resolve()

            with override_settings(BACKUP_DIR=directorio):
                ruta = servicios.validar_ruta(
                    'sacranet_manual_20260101_120000_abcdef.dump'
                )

            self.assertEqual(ruta.parent, directorio)


class AccesoRespaldosTests(SimpleTestCase):

    def crear_solicitud(self, rol):
        solicitud = RequestFactory().get('/backups/')
        solicitud.user = AnonymousUser()
        solicitud.session = {
            'usuario_id': 1,
            'username': 'prueba',
            'rol_nombre': rol,
        }
        solicitud._messages = FallbackStorage(solicitud)

        return solicitud

    def test_administrador_puede_entrar(self):
        def vista(request):
            return HttpResponse('ok')

        respuesta = administrador_requerido(vista)(
            self.crear_solicitud('Administrador')
        )

        self.assertEqual(respuesta.status_code, 200)

    def test_otros_roles_son_redirigidos(self):
        def vista(request):
            return HttpResponse('ok')

        respuesta = administrador_requerido(vista)(
            self.crear_solicitud('Secretaría')
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, '/')

    def test_usuario_sin_sesion_es_redirigido_al_login(self):
        def vista(request):
            return HttpResponse('ok')

        solicitud = RequestFactory().get('/backups/')
        solicitud.user = AnonymousUser()
        solicitud.session = {}

        respuesta = administrador_requerido(vista)(solicitud)

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, '/login/')


class FormatoRespaldosTests(SimpleTestCase):

    def test_formatea_tamanos(self):
        self.assertEqual(
            servicios.formatear_tamano(512),
            '512 B',
        )
        self.assertEqual(
            servicios.formatear_tamano(2048),
            '2.0 KB',
        )
        self.assertEqual(
            servicios.formatear_tamano(5 * 1024 * 1024),
            '5.0 MB',
        )


class RestauracionRespaldosTests(SimpleTestCase):

    def test_pg_restore_recibe_el_nombre_de_la_base_de_datos(self):
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            nombre = 'sacranet_manual_20260101_120000_abcdef.dump'
            (directorio / nombre).write_bytes(b'contenido')

            resultado = SimpleNamespace(
                returncode=0,
                stdout='',
                stderr='',
            )

            with override_settings(
                BACKUP_DIR=directorio,
                DB_ENGINE='postgresql',
                DB_NAME='base_de_prueba',
            ), patch(
                'respaldos.servicios.shutil.which',
                return_value='/usr/bin/pg_restore',
            ), patch(
                'respaldos.servicios._ejecutar',
                return_value=resultado,
            ) as ejecutar, patch(
                'respaldos.servicios.crear_respaldo',
                return_value=directorio / 'seguridad.dump',
            ), patch(
                'respaldos.servicios.connections.close_all',
            ), patch(
                'respaldos.servicios.registrar_historial',
            ), patch(
                'respaldos.servicios._validar_motor',
            ):
                servicios.restaurar_respaldo(nombre, 'tester')

            comando_restauracion = ejecutar.call_args_list[-1].args[0]

            self.assertIn('--dbname', comando_restauracion)
            self.assertIn(
                'base_de_prueba',
                comando_restauracion,
            )
