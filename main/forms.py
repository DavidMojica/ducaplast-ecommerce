from django import forms
from .models import HandlerReparto, TipoUsuario, Usuarios, Clientes, Producto, Pedido
from django.db import models

class FiltrarRecibos(forms.ModelForm):
    id = forms.IntegerField(
        label="Codigo del pedido",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID del pedido'}),
    )
    
    completado_fecha = forms.DateTimeField(
        label='Fecha de completación',
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        input_formats=['%Y-%m-%d'],
    )

    fecha = forms.DateField(
        label='Fecha de venta',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = Pedido
        fields = ['id', 'vendedor', 'cliente', 'completado_fecha']
        labels = {
            'vendedor': 'Vendedor',
            'cliente': 'Cliente',
            'completado_fecha': 'Fecha de completación',
        }
        widgets = {
            'vendedor': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class':'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendedor'].empty_label = 'Cualquiera'
        self.fields['vendedor'].required = False
        self.fields['vendedor'].queryset = Usuarios.objects.filter(tipo_usuario_id__in=[0, 1, 2])

        self.fields['cliente'].empty_label = 'Cualquiera'
        self.fields['cliente'].required = False
        self.fields['cliente'].queryset = Clientes.objects.all()

#Crear o modificar un producto
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['descripcion', 'referencia_fabrica', 'precio', 'cantidad']
        labels = {
            'descripcion': 'Descripción',
            'referencia_fabrica': 'Referencia de fábrica',
            'precio': 'Precio',
            'cantidad': 'Cantidad',
        }
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia_fabrica': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class SeleccionarRepartidor(forms.Form):
    def __init__(self, *args, **kwargs):
        pedido = kwargs.pop('pedido', None)
        super(SeleccionarRepartidor, self).__init__(*args, **kwargs)
        
        repartidores_queryset = Usuarios.objects.filter(tipo_usuario_id=6)
        
        if pedido:
            handler_reparto = HandlerReparto.objects.filter(pedido=pedido).first()
            if handler_reparto:
                repartidor_asignado = handler_reparto.repartidor
                self.fields['repartidor'].queryset = repartidores_queryset
                self.fields['repartidor'].initial = repartidor_asignado.pk  
                
                
                self.fields['repartidorSecundario'].queryset = repartidores_queryset
                
                repartidor_secundario_asignado = HandlerReparto.objects.filter(pedido=pedido).exclude(repartidor=repartidor_asignado).first()
                if repartidor_secundario_asignado:
                    self.fields['repartidorSecundario'].initial = repartidor_secundario_asignado.repartidor.pk
            self.fields['consecutivo'].initial = pedido.consecutivo
            
    repartidor = forms.ModelChoiceField(
        label="Por favor asigne el repartidor que se encargará de esta entrega.",
        widget=forms.Select(attrs={'class': 'form-select', 'placeholder': 'Seleccione repartidor', 'name': 'repartidor', 'id':'repartidor'}),
        queryset=Usuarios.objects.filter(tipo_usuario_id=6),
        empty_label="Seleccione repartidor (Obligatorio)",
        required=True
    )
    
    repartidorSecundario = forms.ModelChoiceField(
        label="Seleccione repartidor secundario si es necesario",
        widget=forms.Select(attrs={'class': 'form-select', 'placeholder': 'Seleccione repartidor secundario', 'name': 'repartidorSecundario', 'id':'repartidorSecundario'}),
        queryset=Usuarios.objects.filter(tipo_usuario_id=6),
        empty_label="Seleccione repartidor secundario (Opcional)",
        required=False
    )
    
    consecutivo = forms.CharField(
        label="Consecutivo del pedido:",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'consecutivo'})
    )



    

class DetallesPedido(forms.Form):
    cliente = forms.ModelChoiceField(
        label="Nombre del cliente",
        widget=forms.Select(attrs={'class': 'form-select', 'placeholder': 'Pablo Perez', 'id': 'cliente'}),
        queryset=Clientes.objects.all(),
        empty_label= "Seleccione el cliente"
    )

    nota = forms.CharField(
        label="Nota",
        widget=forms.Textarea(attrs={'class': 'form-control','id':'nota', 'placeholder': 'Escribe detalles del pedido, de la dirección de entrega o lo que necesites. (500 carácteres máximo).', 'maxlength': '500'})
    )

class ModificarCliente(forms.Form):
    nombre = forms.CharField(
        label="Nombre del cliente",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    direccion = forms.CharField(
        label="Direccion del cliente",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class FiltrarCliente(forms.Form):
    nombre = forms.CharField(
        label="Nombre del usuario",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    id = forms.IntegerField(
        label="Codigo del usuario",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class FiltrarUsuarios(forms.Form):
    nombre = forms.CharField(
        label="Nombre del usuario",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    id = forms.IntegerField(
        label="Codigo del usuario",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tipo_usuario = forms.ModelChoiceField(
        label="Tipo de usuario",
        queryset=TipoUsuario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'tipoUsuario'}),
        empty_label="Todos",
        required=False
    )
    
    def buscar_usuarios_por_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombres = nombre.split()
            if len(nombres) == 1:
                return Usuarios.objects.filter(
                    models.Q(first_name__icontains=nombres[0]) |
                    models.Q(last_name__icontains=nombres[0])
                )
            elif len(nombres) >= 2:
                first_name = nombres[0]
                last_name = ' '.join(nombres[1:])
                return Usuarios.objects.filter(
                    first_name__icontains=first_name,
                    last_name__icontains=last_name
                )
        else:
            return Usuarios.objects.none()

class FiltrarProductos(forms.Form):
    nombre = forms.CharField(
        label="Nombre del producto",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    id = forms.IntegerField(
        label="Codigo de producto",
        required=False,
        min_value=0,
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
    
class RegistroUsuariosForm(forms.ModelForm):
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

class RegistroUsuariosFormAdmin(forms.ModelForm):
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
        queryset=TipoUsuario.objects.exclude(id__in=[0, 1]),
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
  
  
class InicioSesionForm(forms.Form):
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