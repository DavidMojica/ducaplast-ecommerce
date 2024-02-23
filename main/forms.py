from django import forms
from .models import TipoUsuario, Usuarios

class registroUsuariosForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del empleado/administrador'})
    )
    
    last_name = forms.CharField(
        required=False,
        label="Apellidos",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese los apellidos'})
    )
    
    username=forms.CharField(
        required=False,
        label='Documento',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Documento del usuario'})
    )
    
    password = forms.CharField(
        required=False,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    
    usarDocumentoComoPassword = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Usar documento como contraseña"
    )
    
    tipo_usuario=forms.ModelChoiceField(
        required=False,
        label="Tipo de usuario",
        queryset=TipoUsuario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'tipoUsuario'}),
        empty_label="Seleccione tipo de usuario..."
    )
    
    email = forms.EmailField(
        required=False,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Correo electrónico'})
    )
    
    class Meta:
        model = Usuarios
        fields = ('first_name', 'last_name', 'username', 'password', 'usarDocumentoComoPassword', 'tipo_usuario')
    