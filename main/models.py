from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class TipoUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=25)
    
    def __str__(self):
        return self.desc

class Estados(models.Model):
    id = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=25)

    def __str__(self):
            return self.desc
        
class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    dinero_generado = models.BigIntegerField(default=0)
    
    def __str__(self):
            return self.desc
        
# Login model
class Usuarios(AbstractUser):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
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
    
class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=400)
    codigo = models.CharField(max_length=20)
    precio = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=400)
    cantidad = models.IntegerField(default=0)
    
    def __str__(self):
         return self.nombre
     
class ProductosPedido(models.Model):
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)    