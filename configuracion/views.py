from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.utils import timezone

from usuarios.models import Usuario, Rol


def configuracion_view(request):
    # Verificar que el usuario haya iniciado sesión.
    if not request.session.get('usuario_id'):
        return redirect('login')

    # Permitir acceso únicamente al Administrador.
    if request.session.get('rol_nombre') != 'Administrador':
        return redirect('index')

    # Procesar formularios.
    if request.method == 'POST':
        accion = request.POST.get('accion', '')

        # ==========================================
        # CREAR USUARIO
        # ==========================================
        if accion == 'crear_usuario':
            username = request.POST.get(
                'username', ''
            ).strip()

            password = request.POST.get(
                'password', ''
            )

            confirm_password = request.POST.get(
                'confirm_password', ''
            )

            rol_id = request.POST.get('rol_id', '')

            # Validar campos.
            if not username or not password or not rol_id:
                messages.error(
                    request,
                    'Completa todos los campos obligatorios.'
                )

            elif len(username) > 50:
                messages.error(
                    request,
                    'El nombre de usuario no puede superar '
                    'los 50 caracteres.'
                )

            elif Usuario.objects.filter(
                username=username
            ).exists():
                messages.error(
                    request,
                    'Ese nombre de usuario ya existe.'
                )

            elif password != confirm_password:
                messages.error(
                    request,
                    'Las contraseñas no coinciden.'
                )

            elif len(password) < 8:
                messages.error(
                    request,
                    'La contraseña debe tener al menos '
                    '8 caracteres.'
                )

            else:
                try:
                    rol = Rol.objects.get(id_rol=rol_id)

                    with transaction.atomic():
                        Usuario.objects.create(
                            username=username,
                            password_hash=make_password(password),
                            id_rol=rol,
                            creado_en=timezone.now()
                        )

                    messages.success(
                        request,
                        f'El usuario "{username}" '
                        'se creó correctamente.'
                    )

                except Rol.DoesNotExist:
                    messages.error(
                        request,
                        'El rol seleccionado no existe.'
                    )

                except IntegrityError:
                    messages.error(
                        request,
                        'No se pudo crear el usuario. '
                        'Comprueba que el nombre no esté registrado.'
                    )

            return redirect('configuracion')

        # ==========================================
        # CAMBIAR CONTRASEÑA
        # ==========================================
        elif accion == 'cambiar_password':
            id_usuario = request.POST.get(
                'id_usuario', ''
            )

            nueva_password = request.POST.get(
                'nueva_password', ''
            )

            confirmar_password = request.POST.get(
                'confirmar_nueva_password', ''
            )

            if (
                not id_usuario
                or not nueva_password
                or not confirmar_password
            ):
                messages.error(
                    request,
                    'Completa todos los campos para cambiar '
                    'la contraseña.'
                )

            elif nueva_password != confirmar_password:
                messages.error(
                    request,
                    'Las contraseñas no coinciden.'
                )

            elif len(nueva_password) < 8:
                messages.error(
                    request,
                    'La contraseña debe tener al menos '
                    '8 caracteres.'
                )

            else:
                try:
                    usuario = Usuario.objects.get(
                        id_usuario=id_usuario
                    )

                    usuario.password_hash = make_password(
                        nueva_password
                    )

                    usuario.save(
                        update_fields=['password_hash']
                    )

                    messages.success(
                        request,
                        'La contraseña se actualizó correctamente.'
                    )

                except Usuario.DoesNotExist:
                    messages.error(
                        request,
                        'El usuario seleccionado no existe.'
                    )

            return redirect('configuracion')

        else:
            messages.error(
                request,
                'La acción solicitada no es válida.'
            )

            return redirect('configuracion')

    # ==========================================
    # CARGAR INFORMACIÓN PARA LA PÁGINA
    # ==========================================
    usuarios = (
        Usuario.objects
        .select_related('id_rol')
        .order_by('username')
    )

    roles = Rol.objects.order_by('nombre_rol')

    contexto = {
        'usuarios': usuarios,
        'roles': roles,
    }

    return render(
        request,
        'configuracion/configuracion.html',
        contexto
    )