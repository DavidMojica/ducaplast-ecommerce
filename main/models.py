from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission

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
            return self.nombre
        
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

class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    vendedor = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estados, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=300)
    fecha = models.DateTimeField(auto_now_add=True)
    valor = models.IntegerField(default=0)
    nota = models.CharField(max_length=500)
    
    def calcular_valor_pedido(self):
        productos_pedido = ProductosPedido.objects.filter(id_pedido=self)
        return sum([Producto.id_Producto.precio * Producto.cantidad for producto in productos_pedido]) #Valor del pedido
    
    def descontar_cantidad_producto(self):
        productos_pedido = ProductosPedido.objects.filter(id_pedido=self)
        for producto_pedido in productos_pedido:
            producto = producto_pedido.id_producto
            if producto.cantidad < producto_pedido.cantidad:
                raise ValidationError(f"No hay suficiente cantidad disponible para el producto {producto.nombre}.")
            producto.cantidad -= producto_pedido.cantidad
            producto.save()
            
    def actualizar_dinero_generado_cliente(self):
        self.cliente.dinero_generado += self.valor
        self.cliente.save()
            
class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=400)
    referencia_fabrica = models.CharField(max_length=400)
    precio = models.CharField(max_length=20)
    cantidad = models.IntegerField(default=0)
    
    def __str__(self):
         return self.descripcion
     
class ProductosPedido(models.Model):
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)    