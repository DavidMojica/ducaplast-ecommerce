from django.contrib import admin
from .models import Clientes, Usuarios, Pedido, Producto

class ClientesAdmin(admin.ModelAdmin):
    search_fields = ['id', 'nombre']
    
admin.site.register(Clientes, ClientesAdmin)

class UsuariosAdmin(admin.ModelAdmin):
    search_fields = ['id', 'first_name', 'last_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    get_full_name.admin_order_field = 'first_name' 
    get_full_name.short_description = 'Nombre Completo'
    
admin.site.register(Usuarios,UsuariosAdmin)

class PedidoAdmin(admin.ModelAdmin):
    search_fields = ['id']
    
admin.site.register(Pedido, PedidoAdmin)

class ProductoAdmin(admin.ModelAdmin):
    search_fields = ['id', 'descripcion']
    
admin.site.register(Producto, ProductoAdmin)