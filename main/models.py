from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class TipoUsuario(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=25)
    
    def __str__(self):
        return self.description

class Estados(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=25)

    def __str__(self):
            return self.description
        
class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=500, default="")
    #dinero_generado = models.BigIntegerField(default=0)
    
    def __str__(self):
            return f"{self.nombre} ID: {self.id}"
        
# Login model
class Usuarios(AbstractUser):
    id = models.AutoField(primary_key=True)
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, related_name="customuser_set")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_set")
    
    def save(self, *args, **kwargs):
        if not self.password:
            self.set_unusable_password()
        super(Usuarios, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ID: {self.id}"

class TipoProducto(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=25)
    
    def get_bodega_str(self):
        if self.id in [0, 2]: #Desechables, #Varios
            return "Productos de bodega 2"
        elif self.id == 1: #Bolsas
            return "Productos de bodega 1"
        else:
            return "Productos sin tipo"
    
    def get_bodega(self):
        if self.id in [0, 2]: #Desechables, #Varios
            return 2
        elif self.id == 1: #Bolsas
            return 1
        else:
            return 0
        
    def __str__(self):
        return self.description 

class TipoConsecutivo(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=500)
    
    def __str__(self):
        return self.description
    
class TipoCantidad(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=25)
    
    def __str__(self):
        return self.description

class RolReparto(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=25)
    
    def __str__(self):
        return self.description 
    
class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    vendedor = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name="vendedor")
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estados, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)
    nota = models.CharField(max_length=500)
    notaEmpacador = models.CharField(max_length=500, null=True, blank=True)
    empacado_hora = models.DateTimeField(null=True, blank=True)
    facturado_por = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name="facturado_por")
    facturado_hora = models.DateTimeField(null=True, blank=True)
    completado_por = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name="asignador_reparto")
    completado_hora = models.DateTimeField(null=True, blank=True)
    despacho_modificado_hora = models.DateTimeField(null=True, blank=True)
    credito_por = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name="credito_por")
    credito_hora = models.DateTimeField(null=True, blank=True)
    consecutivo = models.CharField(max_length=500, null=True)    
    tipo_consecutivo = models.ForeignKey(TipoConsecutivo, on_delete=models.CASCADE, null=True, blank=True)
    check_bodega = models.BooleanField(default=False, null=False)
    checkeado_por = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name="checkeado_por")
    urgente = models.BooleanField(default=False, null=False)
    
    
    def get_status_tiempo(self):
        if self.completado_por:
            return 'bg-primary'
        current_time = timezone.now()
        pedido_age = current_time - self.fecha
        if pedido_age < timedelta(hours=1):
            return 'bg-success'
        elif timedelta(hours=1) <= pedido_age <= timedelta(hours=3):
            return 'bg-warning'
        else:
            return 'bg-danger'
    
    def get_status_color(self):
        if self.estado_id == 0:
            return 'bg-danger'
        elif self.estado_id in [1,2,4]:
            return 'bg-warning'
        elif self.estado_id in [3,5]:
            return 'bg-primary'
        elif self.estado_id == 6:
            return 'bg-pink'
        else:
            return 'bg-success'
    
    def get_multiple_bodega(self):
        """
        Si contiene el tipo de producto 1 y tiene más de un tipo de producto (len(tipos_productos) > 1), devuelve True.
        Si contiene solo el tipo de producto 1 (len(tipos_productos) == 1), devuelve False.
        Si no contiene el tipo de producto 1, devuelve False

        Returns:
            boolean: boolean
        """
        productos_pedido = ProductosPedido.objects.filter(pedido=self)
        tipos_productos = set(producto.producto.tipo.id for producto in productos_pedido)

        if 1 in tipos_productos:
            if len(tipos_productos) > 1:
                return True
            else:
                return False
        else:
            return False
    
    def get_tiempo_pedido(self):
        if self.completado_hora:
            tiempo_transcurrido = self.completado_hora - self.fecha
            if tiempo_transcurrido:
                days = tiempo_transcurrido.days
                seconds = tiempo_transcurrido.seconds
                hours, remainder = divmod(seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f'Este pedido tomó {days} días, {hours} horas, {minutes} minutos, {seconds} segundos en ser completado.'
            else:
                return 'No se pudo obtener el tiempo empleado.'
        else:
            return 'El pedido no ha sido completado'
            
class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=400)
    referencia_fabrica = models.CharField(max_length=400)
    cantidad = models.IntegerField(default=0)
    tipo = models.ForeignKey(TipoProducto, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
         return self.descripcion 

class ProductosPedido(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    tipo_cantidad = models.ForeignKey(TipoCantidad, on_delete=models.CASCADE, null=True, blank=True)
    paquete = models.CharField(max_length=100, default='', null=True, blank=True)
    peso = models.CharField(max_length=100, default='', null=True, blank=True)

class HandlerEmpaquetacion(models.Model):
    empacador = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE) 
    
class HandlerReparto(models.Model):
    repartidor = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE) 
    rol = models.ForeignKey(RolReparto,on_delete=models.CASCADE, null=True)
    