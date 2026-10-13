import io

from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from confirmacion.views import generar_pdf_confirmacion


class RegistroEmisionConfirmacionTests(SimpleTestCase):

    def test_registra_la_emision_en_historial(self):
        request = RequestFactory().post(
            '/confirmacion/generar-pdf/12/'
        )
        request.session = {'username': 'secretaria'}

        persona = SimpleNamespace(
            id_confirmacion=12,
            nombre='Pedro Ramírez',
        )

        with patch(
            'confirmacion.views.get_object_or_404',
            return_value=persona,
        ), patch(
            'confirmacion.views.generar_constancia_confirmacion',
            return_value=io.BytesIO(b'%PDF-1.4 prueba'),
        ), patch(
            'confirmacion.views.Constancia',
        ) as constancia_mock, patch(
            'confirmacion.views.ConstanciaEmitida',
        ) as historial_mock:

            constancia_mock.objects.filter.return_value \
                .order_by.return_value.first.return_value = None

            instancia = constancia_mock.return_value
            instancia.archivo_pdf.open.return_value = (
                io.BytesIO(b'%PDF-1.4 prueba')
            )

            response = generar_pdf_confirmacion(request, 12)

        historial_mock.objects.using.assert_called_with(
            'historial'
        )

        historial_mock.objects.using.return_value \
            .create.assert_called_once()

        argumentos = (
            historial_mock.objects.using.return_value
            .create.call_args.kwargs
        )

        self.assertEqual(
            argumentos['sacramento'],
            'confirmacion',
        )
        self.assertEqual(
            argumentos['nombre'],
            'Pedro Ramírez',
        )
        self.assertEqual(
            argumentos['usuario'],
            'secretaria',
        )
        self.assertEqual(response.status_code, 200)

    def test_usa_desconocido_sin_sesion(self):
        request = RequestFactory().post(
            '/confirmacion/generar-pdf/12/'
        )
        request.session = {}

        persona = SimpleNamespace(
            id_confirmacion=12,
            nombre='Pedro Ramírez',
        )

        with patch(
            'confirmacion.views.get_object_or_404',
            return_value=persona,
        ), patch(
            'confirmacion.views.generar_constancia_confirmacion',
            return_value=io.BytesIO(b'%PDF-1.4 prueba'),
        ), patch(
            'confirmacion.views.Constancia',
        ) as constancia_mock, patch(
            'confirmacion.views.ConstanciaEmitida',
        ) as historial_mock:

            constancia_mock.objects.filter.return_value \
                .order_by.return_value.first.return_value = None

            instancia = constancia_mock.return_value
            instancia.archivo_pdf.open.return_value = (
                io.BytesIO(b'%PDF-1.4 prueba')
            )

            generar_pdf_confirmacion(request, 12)

        argumentos = (
            historial_mock.objects.using.return_value
            .create.call_args.kwargs
        )

        self.assertEqual(
            argumentos['usuario'],
            'Desconocido',
        )
