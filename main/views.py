from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models.functions import Cast
from django.db.models import FloatField
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import RegistroUsuariosForm, InicioSesionForm, FiltrarProductos, DetallesPedido
from .models import Usuarios, Producto, Clientes, Pedido, ProductosPedido

import re

# Variables
NOMBRELENGTHMIN = 2
APELLIDOSLENGTHMIN = 3
DOCLENGTHMIN = 6 #Minimo de carácteres para el documento
PASSLENGTHMIN = 8 #Minimo de carácteres para la contraseña

carrito = None

EMAILREGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
NUMBERWITHPOINTSREGEX = r'\B(?=(\d{3})+(?!\d))'
#Arrays - listas
adminIds = [0, 1]

#HTTDOCS
HTMLEDITARCUENTA = "editar_cuenta.html"
HTMLHOME = "home.html"
HTMLREGISTRO = "registro.html"
HTMLCATALOGO = "catalogo.html"
HTMLCARRITO = "cart.html"
HTMLORDERS = "orders.html"

#Notificaciones
EXITO_1 = "El usuario ha sido creado correctamente."
EXITO_2 = "Sus datos fueron actualizados correctamente"
EXITO_3 = "Contraseña actualizada correctamente"
ERROR_1 = "El documento que intentó ingresar, ya existe."
ERROR_2 = "Formulario inválido."
ERROR_3 = "Error desconocido."
ERROR_4 = "Usuario o contraseña incorrecta."
ERROR_5 = "Este usuario no pudo ser redireccionado. Comunique este error."
ERROR_6 = "Usuario o documento demasiado corto(s)."
ERROR_7 = "Algun campo quedó vacío."
ERROR_8 = "La contraseña anterior no es la correcta."
ERROR_9 = "Alguna(s) de las contraseñas no cumplen con la longitud minima."
ERROR_10 = "Las contraseñas nuevas no coinciden"
ERROR_11 = "Nombre o apellidos no cumplen con la longitud minima."
ERROR_12 = "Formato de email no válido"

#-----------Functions----------#
#Quita espacio al principio y al final de los campos de un formulario
def stripForm(form):
    for campo in form.fields:
        if isinstance(form.cleaned_data[campo], str):
            form.cleaned_data[campo] = form.cleaned_data[campo].strip()
    return form 

#Verifica que una lista de strings no esté vacía
def isEmpty(elements):
    return any(len(element.strip()) == 0 for element in elements)

#Verifica la validez de un email
def isValidEmail(email):
    if re.match(EMAILREGEX, email):
        return True
    return False

#Agregar punto decimal a los números
def numberWithPoints(numero):
    return re.sub(NUMBERWITHPOINTSREGEX, '.', str(numero))

#Decorador que valida que el usuario no esté logueado para hacer algo.
def unloginRequired(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('registro')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

#Obtener el precio de los articulos del carro y actualizar sus respectivos valores con puntos decimales.
@login_required
def getCartPrice(request):
    carrito = request.session.get('carrito', {})
    total_productos = 0
    if carrito:
        for key, producto in carrito.items():
            total_productos += int(producto['precio']) * int(producto['cantidad'])
            producto['precio_str'] = numberWithPoints(producto['precio'])
            producto['total_producto_str'] = numberWithPoints(producto['total_producto'])
        return total_productos
    
#-------------Views-----------#

@login_required
def Orders(request):
    return render(request, HTMLORDERS)

@unloginRequired
def Home(request):
    newForm = InicioSesionForm()
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            form = stripForm(form)
            
            documento = form.cleaned_data['documento']
            password = form.cleaned_data['password']
            
            #Verificar el minimo de carácteres para cada campo
            if len(documento) < DOCLENGTHMIN or len(password) < PASSLENGTHMIN:
                recycledForm = InicioSesionForm(initial={'documento': documento})
                return render(request, HTMLHOME, {'form': recycledForm,
                                                     'error': ERROR_6})
            
            logedUser = authenticate(request, username=documento, password=password)
            
            #Verificar que el usuario exista y su contraseña sea correcta
            if logedUser is None:
                recycledForm = InicioSesionForm(initial={'documento': documento})
                return render(request, HTMLHOME, {'form': recycledForm,
                                                    'error':ERROR_4})
            else:
                login(request, logedUser)
                userType = logedUser.tipo_usuario_id
                if userType == 0:
                    return redirect(reverse('registro'))
                elif userType == 1:
                    return redirect(reverse('registro'))
                elif userType == 2:
                    return redirect(reverse('registro'))
                elif userType == 3:
                    return redirect(reverse('registro'))
                elif userType == 4:
                    return redirect(reverse('registro'))
                else:
                    logout(request)
                    return render(request, HTMLHOME, {'form': newForm,
                                                         'error': ERROR_5})
        else:
            return render(request, HTMLHOME,{'form':newForm,
                                                'error': ERROR_2})
    return render(request, HTMLHOME, {'form': newForm})

@login_required
def Logout(request):
    logout(request)
    return redirect(reverse('home'))

@login_required
def Registro(request):
    newForm = RegistroUsuariosForm()
    if request.method == "POST":
        form = RegistroUsuariosForm(request.POST)
        #Verificar que el documento no se haya registrado antes.
        if form.has_error("username", code="unique"):
            return render(request, HTMLREGISTRO, {
                    "form": form,
                    "evento": ERROR_1,
                    "exito": False,
                })
        
        #Verificar la validez del formulario (campos en blanco, tipos de datos correctos)
        if form.is_valid():
            #Quitar espacios al principio y al final de los campos de texto
            form = stripForm(form)
            #Guardar el usuario nuevo
            try:
                documento = form.cleaned_data['username']
                password = form.cleaned_data['password']
                
                if len(documento) < DOCLENGTHMIN or len(password) < PASSLENGTHMIN:
                    return render(request, HTMLREGISTRO, {
                      "form": form,
                      "evento": ERROR_6,
                      "exito": False  
                    })
                
                user = form.save(commit=False)
                user.username = documento
                user.set_password(password)
                user.email = form.cleaned_data['email']
                user.save()
                
                return render(request, HTMLREGISTRO, {
                    "form": newForm,
                    "evento": EXITO_1,
                    "exito": True,
                    "documento": f"Usuario login: {documento}",
                    "password": f"Contraseña: {form.cleaned_data['password']}"
                })
            except Exception as e:
                return render(request, HTMLREGISTRO, {
                    "form": form,
                    "evento": ERROR_3,
                    "exito": False,
                })
        else:
            return render(request, HTMLREGISTRO, {
                    "form": form,
                    "evento": ERROR_2,
                    "exito": False,
                })
    #GET
    return render(request, HTMLREGISTRO, {'form': newForm })

@login_required
def EditarCuenta(request):
    user = get_object_or_404(Usuarios, pk=str(request.user.id))
    if request.method == "POST":
        print(request.POST)
        print("nombre" in request.POST)
        print("pass_data" in request.POST)
        if "acc_data" in request.POST:
            nombre = request.POST.get("nombre", "").strip()
            apellidos = request.POST.get("apellidos", "").strip()
            email = request.POST.get("email", "").strip()
            print(f"nombre {nombre}")
            if isEmpty([nombre, apellidos, email]):
                return render(request, HTMLEDITARCUENTA,{"account_data_event": ERROR_7})
            
            if len(nombre) < NOMBRELENGTHMIN or len(apellidos) < APELLIDOSLENGTHMIN:
                return render(request, HTMLEDITARCUENTA, {"account_data_event": ERROR_11})
            
            if not isValidEmail(email):
                return render(request, HTMLEDITARCUENTA, {"account_data_event":ERROR_12})
       
            user.first_name = nombre
            user.last_name = apellidos
            user.email = email
            user.save()
            
            return render(request, HTMLEDITARCUENTA, {"account_data_event": EXITO_2})
            
        elif "pass_data" in request.POST:
            
            oldPassword = request.POST.get('oldPassword')
            newPassword = request.POST.get('password')
            newPassword1 = request.POST.get('password1')
            
            if user.check_password(oldPassword):
                if len(newPassword) >= PASSLENGTHMIN or len(newPassword1) >= PASSLENGTHMIN:
                    if newPassword == newPassword1:
                        user.set_password(newPassword)
                        user.save()
                        return redirect(reverse('home'))
                    else:
                        return render(request, HTMLEDITARCUENTA,{ "password_change_event": ERROR_10 })
                else:
                    return render(request, HTMLEDITARCUENTA,{ "password_change_event": ERROR_9 })
            else:
                return render(request, HTMLEDITARCUENTA, { "password_change_event": ERROR_8 })
    
    
    return render(request, HTMLEDITARCUENTA)

@login_required
def CartHandler(request):
    carrito = request.session.get('carrito', {})
    if request.method == "POST":
        event = ""
        action = request.POST.get('action')
        producto_id = request.POST.get('producto_id')
        
        #Añadir
        if action == "1":
            try:
                producto = Producto.objects.get(pk=producto_id)
                cantidad = int(request.POST.get('cantidad', 1)) 
                total_producto = int(cantidad) * int(producto.precio)
                carrito[producto_id] = {
                    'descripcion': producto.descripcion,
                    'precio': producto.precio,
                    'referencia_fabrica': producto.referencia_fabrica,
                    'cantidad': cantidad,
                    'total_producto': total_producto,
                }
                event = "Producto añadido"
                request.session['carrito'] = carrito
                return JsonResponse({'success': True, 'event': event,})
            except Producto.DoesNotExist:
                event = "El producto no existe"
              
        #Borrar  
        elif action == "2":
            if producto_id in carrito:
                del carrito[producto_id]
                event = "Producto borrado"
                carrito_vacio = len(carrito) == 0  
            total_productos_actualizado = sum(int(item['total_producto']) for item in carrito.values())
            iva_actualizado = total_productos_actualizado * 0.19
            total_actualizado = total_productos_actualizado + iva_actualizado
            request.session['carrito'] = carrito
            
            return JsonResponse({'success': True, 'event': event, 'total_productos': numberWithPoints(total_productos_actualizado),
                                'iva': numberWithPoints(iva_actualizado), 'total_actualizado': numberWithPoints(total_actualizado), 'carrito_vacio': carrito_vacio,
                                'productos_cantidad': len(request.session['carrito'])})
        #borrar todo el carrito
        elif action == "3":
            carrito.clear()
            request.session['carrito'] = carrito
            return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
 
@login_required
def Catalogo(request):
    productos = Producto.objects.order_by('id')
    form = FiltrarProductos(request.GET)
    PRODUCTOS_POR_PAGINA = 18
    
    if form.is_valid():
        id_producto = form.cleaned_data.get('id')
        nombre = form.cleaned_data.get('nombre')
        ordenar = form.cleaned_data.get('ordenar')
        disponibles = form.cleaned_data.get('disponibles')
        
        #--------------Extraer los datos-------------#
        if ordenar:
            if ordenar == '1':
                productos = Producto.objects.order_by('-id')
            elif ordenar == '2':
                productos = Producto.objects.order_by('descripcion')
            elif ordenar == '3':
                productos = Producto.objects.order_by('-descripcion')
            elif ordenar == '4':
                productos = productos.annotate(precio_num=Cast('precio', FloatField())).order_by('-precio_num')
            elif ordenar == '5':
                productos = productos.annotate(precio_num=Cast('precio', FloatField())).order_by('precio_num')
            else: 
                pass
        #----------Filtrar los datos----------#
        if id_producto:
            productos = productos.filter(id=id_producto)
           
        if nombre:
            productos = productos.filter(descripcion__icontains=nombre)
        #Modulo disponibles 
        if disponibles:
            productos = productos.filter(cantidad__gt=0)
        
    
    paginator = Paginator(productos, PRODUCTOS_POR_PAGINA)
    page_number = request.GET.get('page')
    
    try:
        productos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    return render(request, HTMLCATALOGO,{
        'productos': productos_paginados,
        'carrito': request.session.get('carrito', {}),
        'form': form
    })
           
@login_required
def Cart(request):
    #Valor total de los productos
    
    form = DetallesPedido(request.POST)
    # if request.method == "POST":
    carrito = request.session.get('carrito', {})
    total_productos = 0
    iva = 0
    if carrito:
        total_productos = getCartPrice(request)
        iva = int(round(total_productos * 0.19))
        
    if "confirmar_venta" in request.POST:
        print("llego")
        cliente = request.POST.get('cliente')
        pedido_nota = request.POST.get('nota')
        productos = request.POST.get('productos')
        print(f"cliente: {cliente}\nnota:{pedido_nota}\nProductos:{productos}")
        return JsonResponse({'success': True})
    
    elif "crear_cliente" in request.POST:
        nombre = request.POST.get('nombre_cli').strip()
        direccion = request.POST.get('direccion_cli').strip()
        nuevo_cliente = Clientes(nombre=nombre, direccion=direccion)
        nuevo_cliente.save()

        
    
    return render(request, HTMLCARRITO, {'productos':carrito,
                                        'total_productos': numberWithPoints(total_productos),
                                        'iva': numberWithPoints(iva),
                                        'total_venta':numberWithPoints(total_productos+iva),
                                        'cantidad_productos': len(carrito),
                                        'form': form})
    


