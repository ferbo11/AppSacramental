import re

from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from pypdf import PdfReader

from constancias.generador_bautismo import (
    generar_constancia_bautismo,
)
from constancias.generador_matrimonio import (
    generar_constancia_matrimonio,
)
from constancias.utilidades import (
    formatear_fecha_larga,
    numero_a_letras,
    obtener_fecha_emision,
)


def extraer_texto(pdf):
    pdf.seek(0)

    lector = PdfReader(pdf)
    texto = lector.pages[0].extract_text() or ''

    return re.sub(r'\s+', ' ', texto).strip()


def leer_pdf(pdf):
    pdf.seek(0)
    return PdfReader(pdf)


class NumeroALetrasTests(SimpleTestCase):

    def test_convierte_unidades_y_decenas(self):
        self.assertEqual(numero_a_letras(0), 'cero')
        self.assertEqual(numero_a_letras(26), 'veintiséis')
        self.assertEqual(numero_a_letras(99), 'noventa y nueve')

    def test_convierte_anios(self):
        self.assertEqual(numero_a_letras(1000), 'mil')
        self.assertEqual(
            numero_a_letras(1999),
            'mil novecientos noventa y nueve',
        )
        self.assertEqual(
            numero_a_letras(2026),
            'dos mil veintiséis',
        )


class FechaEmisionTests(SimpleTestCase):

    def test_formatea_dia_mes_y_anio_en_letras(self):
        self.assertEqual(
            formatear_fecha_larga(
                date(2026, 10, 26)
            ),
            (
                'a los 26 días del mes de octubre '
                'del año dos mil veintiséis'
            ),
        )

    def test_usa_la_zona_horaria_de_guatemala(self):
        fecha_utc = datetime(
            2026,
            10,
            27,
            3,
            30,
            tzinfo=ZoneInfo('UTC'),
        )

        self.assertEqual(
            obtener_fecha_emision(fecha_utc),
            (
                'a los 26 días del mes de octubre '
                'del año dos mil veintiséis'
            ),
        )

    def test_obtiene_la_fecha_actual_del_servidor(self):
        fecha_servidor = datetime(
            2027,
            1,
            1,
            2,
            0,
            tzinfo=ZoneInfo('UTC'),
        )

        with patch(
            'constancias.utilidades.timezone.now',
            return_value=fecha_servidor,
        ):
            texto = obtener_fecha_emision()

        self.assertEqual(
            texto,
            (
                'a los 31 días del mes de diciembre '
                'del año dos mil veintiséis'
            ),
        )

    def test_la_fecha_de_emision_cambia_con_la_fecha(self):
        primero = formatear_fecha_larga(
            date(2026, 10, 26)
        )
        segundo = formatear_fecha_larga(
            date(2027, 1, 1)
        )

        self.assertNotEqual(primero, segundo)
        self.assertIn('dos mil veintiséis', primero)
        self.assertIn('dos mil veintisiete', segundo)


class GeneradorBautismoTests(SimpleTestCase):

    def crear_pdf(self, fecha_emision=date(2026, 10, 26)):
        return generar_constancia_bautismo(
            {
                'nombre_sacramentado': 'María López García',
                'padre': 'Juan López Pérez',
                'madre': 'Ana García Méndez',
                'padrino_1': 'Carlos López',
                'padrino_2': 'Rosa Méndez',
                'lugar_nacimiento': 'Cobán',
                'departamento': 'Alta Verapaz',
                'libro': 4,
                'folio': 15,
                'numero_partida': 7,
            },
            observacion='Constancia solicitada por la interesada.',
            fecha_emision=fecha_emision,
        )

    def test_pdf_es_valido_y_tamano_carta(self):
        pdf = self.crear_pdf()

        self.assertTrue(
            pdf.getvalue().startswith(b'%PDF')
        )

        pagina = leer_pdf(pdf).pages[0]

        self.assertEqual(
            float(pagina.mediabox.width),
            612,
        )
        self.assertEqual(
            float(pagina.mediabox.height),
            792,
        )

    def test_incluye_datos_en_formato_plantilla(self):
        texto = extraer_texto(self.crear_pdf())

        self.assertIn('Bautismos No. 4', texto)
        self.assertIn('folio 15', texto)
        self.assertIn('partida No. 7', texto)
        self.assertIn('María López García', texto)
        self.assertIn('Juan López Pérez', texto)
        self.assertIn('Ana García Méndez', texto)
        self.assertIn('Carlos López', texto)
        self.assertIn('Rosa Méndez', texto)
        self.assertIn('Cobán', texto)
        self.assertIn('Alta Verapaz', texto)

    def test_incluye_fecha_de_expedicion_y_observaciones(self):
        texto = extraer_texto(self.crear_pdf())

        self.assertIn(
            (
                'Para el uso que al interesado(a) convenga, '
                'se extiende en una hoja de papel bond membretada tamaño carta'
            ),
            texto,
        )
        self.assertIn(
            (
                'a los 26 días del mes de octubre del año '
                'dos mil veintiséis, en la ciudad de '
                'Cobán, Alta Verapaz.'
            ),
            texto,
        )
        self.assertIn(
            'Constancia solicitada por la interesada.',
            texto,
        )

    def test_la_fecha_de_expedicion_cambia_en_el_pdf(self):
        texto_2026 = extraer_texto(
            self.crear_pdf(date(2026, 10, 26))
        )
        texto_2027 = extraer_texto(
            self.crear_pdf(date(2027, 1, 1))
        )

        self.assertIn(
            'dos mil veintiséis',
            texto_2026,
        )
        self.assertIn(
            'dos mil veintisiete',
            texto_2027,
        )

    def test_usa_na_para_partida_si_falta(self):
        pdf = generar_constancia_bautismo(
            {
                'nombre_sacramentado': 'María López García',
                'libro': 4,
                'folio': 15,
            },
            fecha_emision=date(2026, 10, 26),
        )

        texto = extraer_texto(pdf)

        self.assertIn('Bautismos No. 4', texto)
        self.assertIn('folio 15', texto)
        self.assertIn('partida No. N/A', texto)


class GeneradorMatrimonioTests(SimpleTestCase):

    def crear_pdf(self, fecha_emision=date(2026, 10, 26)):
        return generar_constancia_matrimonio(
            {
                'nombre_esposo': 'José Ramírez',
                'nombre_esposa': 'Ana Morales',
                'libro': 2,
                'folio': 8,
                'anio': 2024,
                'edad_esposo': 32,
                'edad_esposa': 29,
                'padre_esposo': 'Ramón Ramírez',
                'madre_esposo': 'Marta Pérez',
                'padre_esposa': 'Luis Morales',
                'madre_esposa': 'Rosa García',
            },
            observacion='Expedida para trámite civil.',
            fecha_emision=fecha_emision,
        )
