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
    