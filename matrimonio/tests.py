from django.test import SimpleTestCase

from .forms import MatrimonioForm
from .models import Matrimonio


class MatrimonioModeloTests(SimpleTestCase):

    def test_estructura_no_administrada(self):
        self.assertFalse(Matrimonio._meta.managed)
        self.assertEqual(Matrimonio._meta.db_table, 'matrimonios')
        self.assertEqual(Matrimonio._meta.pk.name, 'id')

    def test_datos_faltantes_detecta_campos_criticos(self):
        matrimonio = Matrimonio(id=1, esposo='José Ramírez')

        faltantes = matrimonio.datos_faltantes

        self.assertIn('Nombre de la esposa', faltantes)
        self.assertIn('Libro', faltantes)
        self.assertIn('Folio', faltantes)
        self.assertIn('Fecha del matrimonio', faltantes)

    def test_datos_faltantes_vacio_con_registro_completo(self):
        matrimonio = Matrimonio(
            id=1,
            esposo='José Ramírez',
            esposa='Ana Morales',
            libro='2',
            folio=8,
            ano=2024,
            fecha_matrimonio='2024-05-18',
        )

        self.assertEqual(matrimonio.datos_faltantes, [])

    def test_testigos_une_los_nombres_registrados(self):
        matrimonio = Matrimonio(
            testigo_1='Pedro López',
            testigo_2='María López',
        )

        self.assertEqual(
            matrimonio.testigos,
            'Pedro López y María López',
        )


class MatrimonioFormValidacionTests(SimpleTestCase):
    DATOS = {
        'esposo': 'QA_Esposo',
        'esposa': 'QA_Esposa',
        'libro': 'QA-LIBRO',
        'folio': '100',
        'ano': '2015',
        'mes': 'Abril',
        'dia': '12',
        'fecha_matrimonio': '2015-04-12',
    }

    def test_datos_esenciales_son_obligatorios(self):
        formulario = MatrimonioForm({})

        self.assertFalse(formulario.is_valid())
        for campo in ('esposo', 'esposa', 'libro', 'folio'):
            self.assertIn(campo, formulario.errors)
            self.assertIn(
                'obligatorio',
                str(formulario.errors[campo]),
            )
        self.assertIn('__all__', formulario.errors)

    def test_registro_completamente_vacio_es_rechazado(self):
        formulario = MatrimonioForm({})

        self.assertFalse(formulario.is_valid())
        self.assertIn(
            'fecha del matrimonio',
            str(formulario.non_field_errors()),
        )

    def test_edades_negativas_son_rechazadas(self):
        for campo in ('edad_esposo', 'edad_esposa'):
            with self.subTest(campo=campo):
                datos = dict(self.DATOS)
                datos[campo] = '-1'
                formulario = MatrimonioForm(datos)

                self.assertFalse(formulario.is_valid())
                self.assertIn(campo, formulario.errors)
                self.assertIn(
                    'no puede ser negativa',
                    str(formulario.errors[campo]),
                )

    def test_fechas_contradictorias_son_rechazadas(self):
        casos = (
            ({'ano': '2016'}, 'ano'),
            ({'mes': 'Mayo'}, 'mes'),
            ({'dia': '13'}, 'dia'),
            ({'mes': 'Febrero', 'dia': '30'}, 'dia'),
            ({'mes': 'Mes_Inventado'}, 'mes'),
        )

        for cambios, campo in casos:
            with self.subTest(cambios=cambios):
                datos = dict(self.DATOS)
                datos.update(cambios)
                formulario = MatrimonioForm(datos)

                self.assertFalse(formulario.is_valid())
                self.assertIn(campo, formulario.errors)

    def test_fecha_exacta_sin_componentes_es_aceptada(self):
        datos = dict(self.DATOS)
        datos.pop('ano')
        datos.pop('mes')
        datos.pop('dia')
        formulario = MatrimonioForm(datos)

        self.assertTrue(formulario.is_valid(), str(formulario.errors))

    def test_anio_sin_fecha_exacta_es_aceptado(self):
        datos = dict(self.DATOS)
        datos.pop('mes')
        datos.pop('dia')
        datos.pop('fecha_matrimonio')
        formulario = MatrimonioForm(datos)

        self.assertTrue(formulario.is_valid(), str(formulario.errors))

    def test_mes_numerico_valido_es_aceptado(self):
        datos = dict(self.DATOS)
        datos['mes'] = '4'
        formulario = MatrimonioForm(datos)

        self.assertTrue(formulario.is_valid(), str(formulario.errors))
