from unittest.mock import patch

from django.db import connection
from django.test import Client, TransactionTestCase

from bautismo.models import Bautismo
from comunion.models import PrimeraComunion
from confirmacion.models import Confirmacion
from matrimonio.models import Matrimonio


class RegistroSacramentosTests(TransactionTestCase):
    modelos = (Bautismo, PrimeraComunion, Confirmacion, Matrimonio)

    DATOS_BAUTISMO = {
        'nombre_sacramentado': 'QA_Bautismo',
        'padre': 'QA_Padre_B',
        'madre': 'QA_Madre_B',
        'padrino_1': 'QA_Padrino_B1',
        'padrino_2': 'QA_Padrino_B2',
        'fecha_nacimiento': '2001-02-03',
        'fecha_bautismo': '2001-02-10',
        'lugar_nacimiento': 'QA_Lugar_B',
        'departamento': 'QA_Depto_B',
        'folio': '9101',
        'libro': '9202',
        'partida': '9303',
    }

    DATOS_COMUNION = {
        'nombre_sacramentado': 'QA_Comunion',
        'padre': 'QA_Padre_C',
        'madre': 'QA_Madre_C',
        'bautizado_en': 'QA_Parroquia_C',
        'fecha_sacramento': '2010-05-06',
        'folio': '9111',
        'libro': '9211',
    }

    DATOS_CONFIRMACION = {
        'nombre_sacramentado': 'QA_Confirmacion',
        'padre': 'QA_Padre_K',
        'madre': 'QA_Madre_K',
        'padrino_1': 'QA_Padrino_K1',
        'padrino_2': 'QA_Padrino_K2',
        'fecha_sacramento': '2012-07-08',
        'folio': '9333',
        'libro': '9444',
        'partida': '9555',
    }

    DATOS_MATRIMONIO = {
        'esposo': 'QA_Esposo_M',
        'edad_esposo': '30',
        'esposa': 'QA_Esposa_M',
        'edad_esposa': '28',
        'padre_esposo': 'QA_Padre_M1',
        'madre_esposo': 'QA_Madre_M1',
        'padre_esposa': 'QA_Padre_M2',
        'madre_esposa': 'QA_Madre_M2',
        'testigo_1': 'QA_Testigo_M1',
        'testigo_2': 'QA_Testigo_M2',
        'libro': 'QA-LIBRO-M',
        'folio': '9666',
        'ano': '2015',
        'mes': 'Abril',
        'dia': '12',
        'fecha_matrimonio': '2015-04-12',
    }

    URLS = {
        Bautismo: '/sacramentos/bautismo/crear/',
        PrimeraComunion: '/sacramentos/comunion/crear/',
        Confirmacion: '/sacramentos/confirmacion/crear/',
        Matrimonio: '/sacramentos/matrimonio/crear/',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        existentes = set(connection.introspection.table_names())
        cls._modelos_creados = []
        with connection.schema_editor() as editor:
            for modelo in cls.modelos:
                if modelo._meta.db_table not in existentes:
                    editor.create_model(modelo)
                    cls._modelos_creados.append(modelo)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, '_modelos_creados', None):
            with connection.schema_editor() as editor:
                for modelo in reversed(cls._modelos_creados):
                    editor.delete_model(modelo)
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        sesion = self.client.session
        sesion['usuario_id'] = 1
        sesion['username'] = 'QA_AUDITORIA'
        sesion.save()

    def tearDown(self):
        for modelo in reversed(self.modelos):
            modelo._base_manager.all().delete()
        super().tearDown()

    def test_registro_bautismo(self):
        respuesta = self.client.post(
            self.URLS[Bautismo],
            self.DATOS_BAUTISMO,
        )

        self.assertEqual(respuesta.status_code, 302)
        registro = Bautismo.objects.get(
            nombre_sacramentado='QA_Bautismo',
        )
        self.assertEqual(registro.folio, 9101)
        self.assertEqual(registro.libro, 9202)
        self.assertEqual(registro.partida, 9303)
        self.assertEqual(str(registro.fecha_nacimiento), '2001-02-03')
        self.assertEqual(str(registro.fecha_bautismo), '2001-02-10')

    def test_registro_primera_comunion(self):
        respuesta = self.client.post(
            self.URLS[PrimeraComunion],
            self.DATOS_COMUNION,
        )

        self.assertEqual(respuesta.status_code, 302)
        registro = PrimeraComunion.objects.get(
            nombre_sacramentado='QA_Comunion',
        )
        self.assertEqual(registro.folio, 9111)
        self.assertEqual(registro.libro, 9211)
        self.assertEqual(str(registro.fecha_sacramento), '2010-05-06')

    def test_registro_confirmacion(self):
        respuesta = self.client.post(
            self.URLS[Confirmacion],
            self.DATOS_CONFIRMACION,
        )

        self.assertEqual(respuesta.status_code, 302)
        registro = Confirmacion.objects.get(
            nombre_sacramentado='QA_Confirmacion',
        )
        self.assertEqual(registro.folio, 9333)
        self.assertEqual(registro.libro, 9444)
        self.assertEqual(registro.partida, 9555)
        self.assertEqual(str(registro.fecha_sacramento), '2012-07-08')

    def test_registro_matrimonio(self):
        respuesta = self.client.post(
            self.URLS[Matrimonio],
            self.DATOS_MATRIMONIO,
        )

        self.assertEqual(respuesta.status_code, 302)
        registro = Matrimonio.objects.get(esposo='QA_Esposo_M')
        self.assertEqual(registro.esposa, 'QA_Esposa_M')
        self.assertEqual(registro.edad_esposo, 30)
        self.assertEqual(registro.edad_esposa, 28)
        self.assertEqual(registro.libro, 'QA-LIBRO-M')
        self.assertEqual(registro.folio, 9666)
        self.assertEqual(registro.ano, 2015)
        self.assertEqual(registro.mes, 'Abril')
        self.assertEqual(registro.dia, 12)
        self.assertEqual(str(registro.fecha_matrimonio), '2015-04-12')

    def test_validacion_campos_obligatorios(self):
        for modelo in self.modelos:
            with self.subTest(modelo=modelo.__name__):
                antes = modelo.objects.count()
                respuesta = self.client.post(self.URLS[modelo], {})
                formulario = respuesta.context['formulario']

                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(modelo.objects.count(), antes)
                self.assertTrue(formulario.errors)

    def test_validacion_edades_matrimonio(self):
        for campo in ('edad_esposo', 'edad_esposa'):
            with self.subTest(campo=campo):
                datos = dict(self.DATOS_MATRIMONIO)
                datos[campo] = '-5'
                antes = Matrimonio.objects.count()

                respuesta = self.client.post(
                    self.URLS[Matrimonio],
                    datos,
                )

                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(Matrimonio.objects.count(), antes)
                errores = respuesta.context['formulario'].errors
                self.assertIn(campo, errores)
                self.assertIn(
                    'La edad no puede ser negativa.',
                    str(errores[campo]),
                )

    def test_validacion_fechas_matrimonio(self):
        casos = (
            ({'ano': '1999'}, 'ano'),
            ({'mes': 'Junio'}, 'mes'),
            ({'dia': '28'}, 'dia'),
            ({'mes': 'Febrero', 'dia': '30'}, 'dia'),
        )

        for cambios, campo in casos:
            with self.subTest(cambios=cambios):
                datos = dict(self.DATOS_MATRIMONIO)
                datos.update(cambios)
                antes = Matrimonio.objects.count()

                respuesta = self.client.post(
                    self.URLS[Matrimonio],
                    datos,
                )

                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(Matrimonio.objects.count(), antes)
                self.assertIn(
                    campo,
                    respuesta.context['formulario'].errors,
                )

    def test_fecha_exacta_sin_componentes_es_valida(self):
        datos = dict(self.DATOS_MATRIMONIO)
        datos.pop('ano')
        datos.pop('mes')
        datos.pop('dia')

        respuesta = self.client.post(self.URLS[Matrimonio], datos)

        self.assertEqual(respuesta.status_code, 302)
        registro = Matrimonio.objects.get(esposo='QA_Esposo_M')
        self.assertIsNone(registro.ano)
        self.assertIsNone(registro.mes)
        self.assertIsNone(registro.dia)
        self.assertEqual(str(registro.fecha_matrimonio), '2015-04-12')

    def test_edicion_bautismo(self):
        self.client.post(self.URLS[Bautismo], self.DATOS_BAUTISMO)
        registro = Bautismo.objects.get(nombre_sacramentado='QA_Bautismo')
        datos = dict(self.DATOS_BAUTISMO)
        datos['nombre_sacramentado'] = 'QA_Bautismo_Editado'
        datos['fecha_nacimiento'] = '2002-03-04'
        datos['partida'] = '9404'

        respuesta = self.client.post(
            f'/sacramentos/bautismo/{registro.pk}/editar/',
            datos,
        )

        registro.refresh_from_db()
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(registro.nombre_sacramentado, 'QA_Bautismo_Editado')
        self.assertEqual(str(registro.fecha_nacimiento), '2002-03-04')
        self.assertEqual(registro.partida, 9404)
        self.assertEqual(registro.padrino_1, 'QA_Padrino_B1')

    def test_edicion_matrimonio_rechaza_edad_negativa(self):
        self.client.post(self.URLS[Matrimonio], self.DATOS_MATRIMONIO)
        registro = Matrimonio.objects.get(esposo='QA_Esposo_M')
        datos = dict(self.DATOS_MATRIMONIO)
        datos['edad_esposa'] = '-2'

        respuesta = self.client.post(
            f'/sacramentos/matrimonio/{registro.pk}/editar/',
            datos,
        )

        registro.refresh_from_db()
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(registro.edad_esposa, 28)
        self.assertIn(
            'edad_esposa',
            respuesta.context['formulario'].errors,
        )

    def test_manejo_errores_al_crear(self):
        with patch(
            'bautismo.views.logger.exception',
        ) as registrar_error, patch(
            'bautismo.views.BautismoForm.save',
            side_effect=Exception('detalle_tecnico_no_mostrar'),
        ):
            respuesta = self.client.post(
                self.URLS[Bautismo],
                self.DATOS_BAUTISMO,
            )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(registrar_error.called)
        self.assertContains(
            respuesta,
            'No se pudo crear el registro de bautismo.',
        )
        self.assertNotContains(
            respuesta,
            'detalle_tecnico_no_mostrar',
        )

    def test_manejo_errores_al_editar(self):
        self.client.post(self.URLS[Matrimonio], self.DATOS_MATRIMONIO)
        registro = Matrimonio.objects.get(esposo='QA_Esposo_M')

        with patch(
            'matrimonio.views.logger.exception',
        ) as registrar_error, patch(
            'matrimonio.views.MatrimonioForm.save',
            side_effect=Exception('detalle_tecnico_no_mostrar'),
        ):
            respuesta = self.client.post(
                f'/sacramentos/matrimonio/{registro.pk}/editar/',
                self.DATOS_MATRIMONIO,
            )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(registrar_error.called)
        self.assertContains(
            respuesta,
            'No se pudo actualizar el registro de matrimonio.',
        )
        self.assertNotContains(
            respuesta,
            'detalle_tecnico_no_mostrar',
        )
