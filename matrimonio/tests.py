from django.test import SimpleTestCase

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
