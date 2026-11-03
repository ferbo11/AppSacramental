from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.messages.middleware import MessageMiddleware
from django.test import RequestFactory, SimpleTestCase

from .models import Usuario
from .views import login_view


class LoginViewTests(SimpleTestCase):

    def crear_request(self, username, password):
        request = RequestFactory().post(
            '/login/',
            data={
                'username': username,
                'password': password,
            },
        )
        request.session = {}
        MessageMiddleware(lambda req: None)(request)

        return request

    def usuario_de_prueba(self):
        return SimpleNamespace(
            id_usuario=1,
            username='secretaria',
            password_hash='hash_de_prueba',
            id_rol_id=2,
            id_rol=SimpleNamespace(nombre_rol='Secretaria'),
        )

    def autenticar(self, username, password, usuario=None, coincide=False):
        with patch(
            'usuarios.views.Usuario.objects.select_related',
        ) as select_related, patch(
            'usuarios.views.check_password',
            return_value=coincide,
        ):
            if usuario is None:
                select_related.return_value.get.side_effect = (
                    Usuario.DoesNotExist
                )
            else:
                select_related.return_value.get.return_value = usuario

            return login_view(
                self.crear_request(username, password)
            )

    def test_usuario_incorrecto_muestra_el_popup(self):
        response = self.autenticar(
            'no_existe',
            'clave',
        )

        contenido = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Usuario o contraseña incorrectos', contenido)
        self.assertIn('login-modal', contenido)
        self.assertIn('Entendido', contenido)

    def test_contrasena_incorrecta_muestra_el_popup(self):
        response = self.autenticar(
            'secretaria',
            'clave_incorrecta',
            usuario=self.usuario_de_prueba(),
            coincide=False,
        )

        contenido = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Usuario o contraseña incorrectos', contenido)
        self.assertIn('login-modal', contenido)

    def test_ambos_campos_incorrectos_muestran_el_popup(self):
        response = self.autenticar(
            'no_existe',
            'clave_incorrecta',
        )

        contenido = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Usuario o contraseña incorrectos', contenido)
        self.assertIn('login-modal', contenido)

    def test_campos_vacios_muestran_el_popup(self):
        response = self.autenticar('', '')

        contenido = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Usuario o contraseña incorrectos', contenido)
        self.assertIn('login-modal', contenido)

    def test_login_exitoso_redirige_y_guarda_la_sesion(self):
        request = self.crear_request(
            'secretaria',
            'clave_correcta',
        )

        with patch(
            'usuarios.views.Usuario.objects.select_related',
        ) as select_related, patch(
            'usuarios.views.check_password',
            return_value=True,
        ):
            select_related.return_value.get.return_value = (
                self.usuario_de_prueba()
            )

            response = login_view(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(request.session['usuario_id'], 1)
        self.assertEqual(request.session['username'], 'secretaria')
        self.assertEqual(request.session['rol_id'], 2)
        self.assertEqual(request.session['rol_nombre'], 'Secretaria')

    def test_popup_no_aparece_sin_error(self):
        request = RequestFactory().get('/login/')
        request.session = {}

        response = login_view(request)

        contenido = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('role="alertdialog"', contenido)
        self.assertNotIn('Usuario o contraseña incorrectos', contenido)
