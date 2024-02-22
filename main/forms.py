from django import forms
from .models import TipoUsuario, Usuarios

class registroUsuariosForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del empleado/administrador'})
    )
    
    documento=forms.CharField(
        label='Documento',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Documento del usuario'})
    )
    
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    
    usarDocumentoComoPassword = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Usar documento como contraseña"
    )
    
    tipo_usuario=forms.ModelChoiceField(
        label="Tipo de usuario",
        queryset=TipoUsuario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'tipoUsuario'}),
        empty_label="Seleccione tipo de usuario..."
    )
    
    class Meta:
        model = Usuarios
        fields = ('nombre', 'documento', 'password', 'usarDocumentoComoPassword', 'tipo_usuario')
    