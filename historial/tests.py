import json
import re

from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase, TestCase
from django.utils import timezone

from historial.management.commands.importar_constancias import (
    construir_registro,
    normalizar_tipo,
)
from historial.models import ConstanciaEmitida
from AppSacramental.views import index


def extraer_json(response, script_id):
    contenido = response.content.decode()

    patron = (
        r'<script id="%s" type="application/json">(.*?)</script>'
        % re.escape(script_id)
    )

    coincidencia = re.search(patron, contenido, re.S)

    if coincidencia is None:
        raise AssertionError(
            f'No se encontró el json_script "{script_id}"'
        )

    return json.loads(coincidencia.group(1))


class ImportacionHistoricaTests(SimpleTestCase):

    def test_normaliza_los_cuatro_tipos(self):
        self.assertEqual(normalizar_tipo('Bautismo'), 'bautismo')
        self.assertEqual(
            normalizar_tipo('Primera Comunión'),
            'comunion',
        )
        self.assertEqual(
            normalizar_tipo('Confirmación'),
            'confirmacion',
        )
        self.assertEqual(
            normalizar_tipo('Matrimonio'),
            'matrimonio',
        )

    def test_tipo_desconocido_devuelve_none(self):
        self.assertIsNone(normalizar_tipo('Otro'))
        self.assertIsNone(normalizar_tipo(None))

    def test_construir_registro_recorta_y_mapea(self):
        constancia = SimpleNamespace(
            tipo_sacramento='Confirmación',
            nombre_persona='X' * 250,
            usuario_emisor='Y' * 200,
            fecha_emision=timezone.now(),
        )

        registro = construir_registro(constancia)

        self.assertEqual(registro['sacramento'], 'confirmacion')
        self.assertEqual(len(registro['nombre']), 200)
        self.assertEqual(len(registro['usuario']), 150)

    def test_construir_registro_usa_desconocido(self):
        constancia = SimpleNamespace(
            tipo_sacramento='Bautismo',
            nombre_persona='Ana',
            usuario_emisor=None,
            fecha_emision=timezone.now(),
        )

        registro = construir_registro(constancia)

        self.assertEqual(registro['usuario'], 'Desconocido')


class ConstanciaEmitidaModeloTests(TestCase):
    databases = {'default', 'historial'}

    def test_el_router_guarda_en_la_base_historial(self):
        ConstanciaEmitida.objects.create(
            nombre='Ana López',
            sacramento='comunion',
            usuario='secretaria',
        )

        self.assertEqual(
            ConstanciaEmitida.objects.using('historial').count(),
            1,
        )

    def test_str_usa_el_nombre_legible(self):
        registro = ConstanciaEmitida(
            nombre='Ana López',
            sacramento='bautismo',
            usuario='secretaria',
        )

        self.assertEqual(
            str(registro),
            'Bautismo - Ana López',
        )


class DashboardIndexTests(TestCase):
    databases = {'default', 'historial'}

    def llamar_index(self):
        request = RequestFactory().get('/')
        request.session = {'usuario_id': 1}
        return index(request)

    def test_sin_datos_las_graficas_muestran_cero(self):
        response = self.llamar_index()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            extraer_json(response, 'datos-sacramentos'),
            [0, 0, 0, 0],
        )

        self.assertEqual(
            extraer_json(response, 'datos-meses'),
            [0] * 12,
        )

        self.assertIn(
            'No hay constancias generadas',
            response.content.decode(),
        )

    def test_incluye_cuatro_sacramentos_y_doce_meses(self):
        response = self.llamar_index()

        self.assertEqual(
            extraer_json(response, 'etiquetas-sacramentos'),
            [
                'Bautismo',
                'Primera Comunión',
                'Confirmación',
                'Matrimonio',
            ],
        )

        self.assertEqual(
            len(extraer_json(response, 'etiquetas-meses')),
            12,
        )

    def test_cuenta_por_sacramento_y_por_mes(self):
        ConstanciaEmitida.objects.using('historial').create(
            nombre='Uno',
            sacramento='bautismo',
            usuario='secretaria',
        )
        ConstanciaEmitida.objects.using('historial').create(
            nombre='Dos',
            sacramento='bautismo',
            usuario='secretaria',
        )
        ConstanciaEmitida.objects.using('historial').create(
            nombre='Tres',
            sacramento='confirmacion',
            usuario='secretaria',
        )

        response = self.llamar_index()

        self.assertEqual(
            extraer_json(response, 'datos-sacramentos'),
            [2, 0, 1, 0],
        )

        datos_meses = extraer_json(response, 'datos-meses')

        self.assertEqual(len(datos_meses), 12)
        self.assertEqual(sum(datos_meses), 3)

        mes_actual = timezone.localdate().month
        self.assertEqual(datos_meses[mes_actual - 1], 3)

    def test_muestra_el_historial_reciente_en_la_tabla(self):
        ConstanciaEmitida.objects.using('historial').create(
            nombre='Ana López',
            sacramento='comunion',
            usuario='secretaria',
        )

        response = self.llamar_index()
        contenido = response.content.decode()

        self.assertIn('Ana López', contenido)
        self.assertIn('Primera Comunión', contenido)
        self.assertIn('secretaria', contenido)
        self.assertNotIn(
            'No hay constancias generadas',
            contenido,
        )
