import re

from django import forms
from .models import TipoUsuario, Usuarios

class filtrarProductos(forms.Form):
    nombre = forms.CharField(
        label="Nombre del producto",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    id = forms.IntegerField(
        label="Codigo de producto",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    disponibles = forms.BooleanField(
        label="Sólo productos disponibles",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    OPCIONES = (('0', 'Código de producto (Menor a mayor)'),
                ('1', 'Código de producto (Mayor a menor)'),
                ('2', 'Alfabéticamente (A-Z)'),
                ('3', 'Alfabéticamente (Z-A)'),
                ('4', 'Precio (Mayor a menor)'),
                ('5', 'Precio (Menor a mayor)'))
    
    ordenar = forms.ChoiceField(
        label="Ordenar por:",
        choices=OPCIONES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='0',
    )
    

class registroUsuariosForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del empleado/administrador', 'id': 'nombre'})
    )
    
    last_name = forms.CharField(
        label="Apellidos",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese los apellidos', 'id':'apellidos'})
    )
    
    username=forms.CharField(
        label='Documento',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Documento del usuario', 'id':'documento'})
    )
    
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña', 'id': 'password'})
    )
    
    usarDocumentoComoPassword = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id':'copyUsername'}),
        label="Usar documento como contraseña"
    )
    
    tipo_usuario=forms.ModelChoiceField(
        label="Tipo de usuario",
        queryset=TipoUsuario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'tipoUsuario'}),
        empty_label="Seleccione tipo de usuario..."
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Correo electrónico', 'id': 'email'})
    )
    
    class Meta:
        model = Usuarios
        fields = ('first_name', 'last_name', 'username', 'password', 'usarDocumentoComoPassword', 'tipo_usuario')
    
class inicioSesionForm(forms.Form):
    documento = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Documento', 'id':'documento'}),
        required=True
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Contraseña', 'id':'password'}),
        required=True
    )   
    
    class Meta:
        fields = ('documento','password')