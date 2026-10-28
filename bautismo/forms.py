from django import forms

from .models import Bautismo


class BautismoForm(forms.ModelForm):
    class Meta:
        model = Bautismo
        fields = [
            'nombre_sacramentado',
            'padre',
            'madre',
            'padrino_1',
            'padrino_2',
            'lugar_nacimiento',
            'departamento',
            'folio',
            'libro',
            'requiere_revision',
        ]
        labels = {
            'nombre_sacramentado': 'Nombre del sacramentado',
            'padre': 'Padre',
            'madre': 'Madre',
            'padrino_1': 'Padrino 1',
            'padrino_2': 'Padrino 2',
            'lugar_nacimiento': 'Lugar de nacimiento',
            'departamento': 'Departamento',
            'folio': 'Folio',
            'libro': 'Libro',
            'requiere_revision': 'Requiere revisión',
        }
        widgets = {
            'nombre_sacramentado': forms.TextInput(attrs={'class': 'form-control'}),
            'padre': forms.TextInput(attrs={'class': 'form-control'}),
            'madre': forms.TextInput(attrs={'class': 'form-control'}),
            'padrino_1': forms.TextInput(attrs={'class': 'form-control'}),
            'padrino_2': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'folio': forms.NumberInput(attrs={'class': 'form-control'}),
            'libro': forms.NumberInput(attrs={'class': 'form-control'}),
            'requiere_revision': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields:
            if campo != 'requiere_revision':
                self.fields[campo].widget.attrs.setdefault('class', 'form-control')
