import io

from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from comunion.views import generar_pdf_comunion


class RegistroEmisionComunionTests(SimpleTestCase):

    def test_registra_la_emision_en_historial(self):
        request = RequestFactory().post(
            '/comunion/generar-pdf/7/'
        )
        request.session = {'username': 'secretaria'}

        persona = SimpleNamespace(
            id_comunion=7,
            nombre='Ana López',
        )

        with patch(
            'comunion.views.get_object_or_404',
            return_value=persona,
        ), patch(
            'comunion.views.generar_constancia_comunion',
            return_value=io.BytesIO(b'%PDF-1.4 prueba'),
        ), patch(
            'comunion.views.Constancia',
        ) as constancia_mock, patch(
            'comunion.views.ConstanciaEmitida',
        ) as historial_mock:

            constancia_mock.objects.filter.return_value \
                .order_by.return_value.first.return_value = None

            instancia = constancia_mock.return_value
            instancia.archivo_pdf.open.return_value = (
                io.BytesIO(b'%PDF-1.4 prueba')
            )

            response = generar_pdf_comunion(request, 7)

        historial_mock.objects.using.assert_called_with(
            'historial'
        )

        historial_mock.objects.using.return_value \
            .create.assert_called_once()

        argumentos = (
            historial_mock.objects.using.return_value
            .create.call_args.kwargs
        )

        self.assertEqual(argumentos['sacramento'], 'comunion')
        self.assertEqual(argumentos['nombre'], 'Ana López')
        self.assertEqual(argumentos['usuario'], 'secretaria')
        self.assertEqual(len(argumentos['nombre']), len('Ana López'))
        self.assertEqual(response.status_code, 200)

    def test_usa_desconocido_sin_sesion(self):
        request = RequestFactory().post(
            '/comunion/generar-pdf/7/'
        )
        request.session = {}

        persona = SimpleNamespace(
            id_comunion=7,
            nombre='Ana López',
        )

        with patch(
            'comunion.views.get_object_or_404',
            return_value=persona,
        ), patch(
            'comunion.views.generar_constancia_comunion',
            return_value=io.BytesIO(b'%PDF-1.4 prueba'),
        ), patch(
            'comunion.views.Constancia',
        ) as constancia_mock, patch(
            'comunion.views.ConstanciaEmitida',
        ) as historial_mock:

            constancia_mock.objects.filter.return_value \
                .order_by.return_value.first.return_value = None

            instancia = constancia_mock.return_value
            instancia.archivo_pdf.open.return_value = (
                io.BytesIO(b'%PDF-1.4 prueba')
            )

            generar_pdf_comunion(request, 7)

        argumentos = (
            historial_mock.objects.using.return_value
            .create.call_args.kwargs
        )

        self.assertEqual(
            argumentos['usuario'],
            'Desconocido',
        )
