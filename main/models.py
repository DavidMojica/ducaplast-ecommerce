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
    direccion = models.CharField(max_length=200, default="")
    dinero_generado = models.BigIntegerField(default=0)
    
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
    direccion = models.CharField(max_length=300)
    fecha = models.DateTimeField(auto_now_add=True)
    valor = models.IntegerField(default=0)
    nota = models.CharField(max_length=500)
    notaEmpacador = models.CharField(max_length=500, null=True, blank=True)
    empacado_hora = models.DateTimeField(null=True, blank=True)
    facturado_por = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name="facturado_por")
    facturado_hora = models.DateTimeField(null=True, blank=True)
    despachador_reparto = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name="asignador_reparto")
    despacho_hora = models.DateTimeField(null=True, blank=True)
    despacho_modificado_hora = models.DateTimeField(null=True, blank=True)
    completado_por = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name="completado_por")
    completado_hora = models.DateTimeField(null=True, blank=True)
    consecutivo = models.CharField(max_length=20, null=True, unique=True)    
    
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
        elif self.estado_id in [1,2]:
            return 'bg-warning'
        elif self.estado_id in [3,4]:
            return 'bg-primary'
        else:
            return 'bg-success'
    
    #Modulo cantidad
    # def descontar_cantidad_producto(self):
    #     productos_pedido = ProductosPedido.objects.filter(id_pedido=self)
    #     for producto_pedido in productos_pedido:
    #         producto = producto_pedido.id_producto
    #         if producto.cantidad < producto_pedido.cantidad:
    #             raise ValidationError(f"No hay suficiente cantidad disponible para el producto {producto.nombre}.")
    #         producto.cantidad -= producto_pedido.cantidad
    #         producto.save()
            
    def actualizar_dinero_generado_cliente(self):
        self.cliente.dinero_generado += self.valor
        self.cliente.save()
            
class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=400)
    referencia_fabrica = models.CharField(max_length=400)
    precio = models.CharField(max_length=20)
    cantidad = models.IntegerField(default=0)
    tipo = models.ForeignKey(TipoProducto, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
         return self.descripcion 

class ProductosPedido(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)   
    
class HandlerEmpaquetacion(models.Model):
    empacador = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE) 
    
class HandlerReparto(models.Model):
    repartidor = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE) 
    rol = models.ForeignKey(RolReparto,on_delete=models.CASCADE, null=True)
    