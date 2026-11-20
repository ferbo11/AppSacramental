from datetime import date

from django import forms

from constancias.utilidades import MESES

from .models import Matrimonio


def _numero_mes(valor):
    texto = str(valor or '').strip().lower()
    if not texto:
        return None
    if texto.isdigit():
        numero = int(texto)
        return numero if 1 <= numero <= 12 else None
    if texto in MESES:
        return MESES.index(texto) + 1
    return None


class MatrimonioForm(forms.ModelForm):
    CAMPOS_ESENCIALES = ('esposo', 'esposa', 'libro', 'folio')

    class Meta:
        model = Matrimonio
        fields = [
            'esposo',
            'edad_esposo',
            'esposa',
            'edad_esposa',
            'libro',
            'folio',
            'ano',
            'mes',
            'dia',
            'fecha_matrimonio',
            'padre_esposo',
            'madre_esposo',
            'padre_esposa',
            'madre_esposa',
            'testigo_1',
            'testigo_2',
            'requiere_revision',
        ]
        labels = {
            'esposo': 'Esposo',
            'edad_esposo': 'Edad del esposo',
            'esposa': 'Esposa',
            'edad_esposa': 'Edad de la esposa',
            'libro': 'Libro',
            'folio': 'Folio',
            'ano': 'Año',
            'mes': 'Mes',
            'dia': 'Día',
            'fecha_matrimonio': 'Fecha de matrimonio',
            'padre_esposo': 'Padre del esposo',
            'madre_esposo': 'Madre del esposo',
            'padre_esposa': 'Padre de la esposa',
            'madre_esposa': 'Madre de la esposa',
            'testigo_1': 'Primer testigo',
            'testigo_2': 'Segundo testigo',
            'requiere_revision': 'Requiere revisión',
        }
        widgets = {
            'esposo': forms.TextInput(attrs={'class': 'form-control'}),
            'edad_esposo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'esposa': forms.TextInput(attrs={'class': 'form-control'}),
            'edad_esposa': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'libro': forms.TextInput(attrs={'class': 'form-control'}),
            'folio': forms.NumberInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'mes': forms.TextInput(attrs={'class': 'form-control'}),
            'dia': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_matrimonio': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'padre_esposo': forms.TextInput(attrs={'class': 'form-control'}),
            'madre_esposo': forms.TextInput(attrs={'class': 'form-control'}),
            'padre_esposa': forms.TextInput(attrs={'class': 'form-control'}),
            'madre_esposa': forms.TextInput(attrs={'class': 'form-control'}),
            'testigo_1': forms.TextInput(attrs={'class': 'form-control'}),
            'testigo_2': forms.TextInput(attrs={'class': 'form-control'}),
            'requiere_revision': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.CAMPOS_ESENCIALES:
            self.fields[campo].required = True
            self.fields[campo].error_messages['required'] = (
                'Este dato es obligatorio para registrar el matrimonio.'
            )

    def clean(self):
        cleaned = super().clean()

        for campo in self.CAMPOS_ESENCIALES:
            if campo not in cleaned:
                continue
            valor = cleaned[campo]
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                self.add_error(
                    campo,
                    'Este dato es obligatorio para registrar el matrimonio.',
                )

        for campo in ('edad_esposo', 'edad_esposa'):
            valor = cleaned.get(campo)
            if valor is not None and valor < 0:
                self.add_error(campo, 'La edad no puede ser negativa.')

        fecha = cleaned.get('fecha_matrimonio')
        ano = cleaned.get('ano')
        dia = cleaned.get('dia')
        texto_mes = cleaned.get('mes')
        mes = _numero_mes(texto_mes)

        if texto_mes and mes is None:
            self.add_error(
                'mes',
                'Indique un mes válido, por ejemplo Mayo o 5.',
            )

        if dia is not None and mes is None and fecha is None:
            self.add_error(
                'dia',
                'Si indica el día, debe indicar también el mes.',
            )

        if mes is not None and dia is not None:
            anio_referencia = ano or (fecha.year if fecha else 2000)
            try:
                date(anio_referencia, mes, dia)
            except ValueError:
                self.add_error(
                    'dia',
                    'La combinación de año, mes y día no es una fecha válida.',
                )

        if fecha is not None:
            if ano is not None and ano != fecha.year:
                self.add_error(
                    'ano',
                    'El año no coincide con la fecha de matrimonio.',
                )
            if mes is not None and mes != fecha.month:
                self.add_error(
                    'mes',
                    'El mes no coincide con la fecha de matrimonio.',
                )
            if dia is not None and dia != fecha.day:
                self.add_error(
                    'dia',
                    'El día no coincide con la fecha de matrimonio.',
                )
        elif ano is None and not texto_mes and dia is None:
            self.add_error(
                None,
                'Debe registrar la fecha del matrimonio o al menos el año, '
                'el mes y el día.',
            )

        return cleaned
