from django import forms

from .models import Confirmacion


class ConfirmacionForm(forms.ModelForm):
    class Meta:
        model = Confirmacion
        fields = [
            'nombre_sacramentado',
            'padre',
            'madre',
            'padrino_1',
            'padrino_2',
            'fecha_sacramento',
            'folio',
            'libro',
            'partida',
            'requiere_revision',
        ]
        labels = {
            'nombre_sacramentado': 'Nombre del sacramentado',
            'padre': 'Padre',
            'madre': 'Madre',
            'padrino_1': 'Padrino 1',
            'padrino_2': 'Padrino 2',
            'fecha_sacramento': 'Fecha del sacramento',
            'folio': 'Folio',
            'libro': 'Libro',
            'partida': 'Partida',
            'requiere_revision': 'Requiere revisión',
        }
        widgets = {
            'nombre_sacramentado': forms.TextInput(attrs={'class': 'form-control'}),
            'padre': forms.TextInput(attrs={'class': 'form-control'}),
            'madre': forms.TextInput(attrs={'class': 'form-control'}),
            'padrino_1': forms.TextInput(attrs={'class': 'form-control'}),
            'padrino_2': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_sacramento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'folio': forms.NumberInput(attrs={'class': 'form-control'}),
            'libro': forms.NumberInput(attrs={'class': 'form-control'}),
            'partida': forms.NumberInput(attrs={'class': 'form-control'}),
            'requiere_revision': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
