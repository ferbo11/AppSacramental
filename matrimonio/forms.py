from django import forms

from .models import Matrimonio


class MatrimonioForm(forms.ModelForm):
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
            'fecha_matrimonio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'padre_esposo': forms.TextInput(attrs={'class': 'form-control'}),
            'madre_esposo': forms.TextInput(attrs={'class': 'form-control'}),
            'padre_esposa': forms.TextInput(attrs={'class': 'form-control'}),
            'madre_esposa': forms.TextInput(attrs={'class': 'form-control'}),
            'testigo_1': forms.TextInput(attrs={'class': 'form-control'}),
            'testigo_2': forms.TextInput(attrs={'class': 'form-control'}),
            'requiere_revision': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
