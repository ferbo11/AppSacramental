from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password

from .models import Usuario


def login_view(request):
    if request.session.get('usuario_id'):
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                username=username
            )

            if check_password(password, usuario.password_hash):
                # Guardamos nuestro usuario en la sesión
                request.session['usuario_id'] = usuario.id_usuario
                request.session['username'] = usuario.username
                request.session['rol_id'] = usuario.id_rol_id
                request.session['rol_nombre'] = (
                    usuario.id_rol.nombre_rol
                    if usuario.id_rol
                    else None
                )

                return redirect('index')

        except Usuario.DoesNotExist:
            pass

        return render(
            request,
            'usuarios/login.html',
            {'error': 'Usuario o contraseña incorrectos.'}
        )

    return render(request, 'usuarios/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')