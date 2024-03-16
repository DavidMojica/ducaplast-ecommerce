from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models.functions import Cast
from django.db.models import FloatField
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import RegistroUsuariosForm, InicioSesionForm, FiltrarProductos, DetallesPedido, SeleccionarRepartidor
from .models import Estados, Usuarios, Producto, Clientes, Pedido, ProductosPedido, HandlerDespacho

import re, json

# Variables
NOMBRELENGTHMIN = 2
APELLIDOSLENGTHMIN = 3
DOCLENGTHMIN = 6 #Minimo de carácteres para el documento
PASSLENGTHMIN = 8 #Minimo de carácteres para la contraseña
TIPOREPARTIDOR = 6

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
HTMLORDERDETAIL = "order_detail.html"

#Notificaciones
EXITO_1 = "El usuario ha sido creado correctamente."
EXITO_2 = "Sus datos fueron actualizados correctamente"
EXITO_3 = "Contraseña actualizada correctamente"
EXITO_4 = "El usuario se ha creado correctamente, pero como es repartidor no tiene acceso al sistema todavía."
EXITO_5 = "El repartidor se actualizó correctamente"
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
ERROR_13 = "Acceso no autorizado"
ERROR_14 = "Usted no puede marcar este pedido como completo porque usted no estaba ayudando en el despacho del pedido"
ERROR_15 = "Usted ya está ayudando en el despacho de este pedido"
ERROR_16 = "Su cuenta está desactivada. Contacte con el administrador."
ERROR_17 = "Este pedido ya fue facturado por alguien más"
ERROR_18 = "Este pedido ya fue marcado como despachado por alguien más"
ERROR_19 = "El repartidor de este pedido ya fue elegido por alguien más"
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
    
    
@login_required
def ayudarEnDespacho(request, user, pedido):
    print(f"{user} {pedido}")
    handler = HandlerDespacho(despachador = user, pedido = pedido)
    handler.save()
    
#-------------Views-----------#
@login_required
def OrderDetail(request, order):
    user = get_object_or_404(Usuarios, pk=request.user.id)
    issue = ""
    print(user.tipo_usuario)
    #Post
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        pedido = get_object_or_404(Pedido, pk=order)
        if user.tipo_usuario_id == 3 or user.tipo_usuario in adminIds: #Despachadores
            if pedido.estado_id == 0 and "confirmar_despacho" in request.POST:
                pedido.estado_id = 1
                pedido.save()
                ayudarEnDespacho(request, user, pedido)
                
            elif 'ayudarDespacho' in request.POST:
                despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido) 
                if not despachadores_activos.filter(despachador_id=user.id).exists():
                    ayudarEnDespacho(request, user, pedido)
                else:
                    issue = ERROR_15
            elif 'completarDespacho' in request.POST:
                despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido) 
                if not pedido.estado_id >= 2:
                    if despachadores_activos.filter(despachador_id=user.id).exists():
                        total_productos_actualizado = sum(int(item['total_producto']) for item in carrito.values())
                        iva_actualizado = total_productos_actualizado * 0.19
                        total_actualizado = round(total_productos_actualizado + iva_actualizado)
                        
                        pedido.estado_id = 2
                        pedido.valor =total_actualizado
                        pedido.despachado_hora = timezone.now()
                        pedido.save()
                    else:
                        issue = ERROR_14
                else:
                    issue = ERROR_18
            elif 'modificarProductos' in request.POST:
                productosModificados = request.POST.get('productos')
                try:
                    productosModificados = json.loads(productosModificados)
                except json.JSONDecodeError:
                    return JsonResponse({'success': False, 'msg': "JSON no válido"})
                
                if not productosModificados:
                    return JsonResponse({'success': False, 'msg': "No hay productos en el pedido."})

                carrito.clear()
                request.session['carrito'] = carrito
                productosEnPedido = ProductosPedido.objects.filter(pedido=pedido)
                
                for producto_id, cantidad in productosModificados.items():
                    producto_real = get_object_or_404(Producto, pk=producto_id)
                    carrito[producto_id] = {
                        'precio': producto_real.precio,
                        'cantidad_existencias': producto_real.cantidad,
                        'cantidad': cantidad,
                        'total_producto': int(cantidad) * int(producto_real.precio)
                    }
                    
                    # Actualizar los objetos ProductosPedido
                    producto_en_pedido = productosEnPedido.get(producto=producto_real)
                    producto_en_pedido.cantidad = cantidad
                    producto_en_pedido.total_producto = int(cantidad) * producto_real.precio
                    producto_en_pedido.save()
                    
                    
                total_productos_actualizado = sum(int(item['total_producto']) for item in carrito.values())
                iva_actualizado = total_productos_actualizado * 0.19
                total_actualizado = round(total_productos_actualizado + iva_actualizado)
                request.session['carrito'] = carrito
                return JsonResponse({'success': True, 'total_actualizado': numberWithPoints(total_actualizado)})
            elif 'borrarProducto' in request.POST:
                producto_id = request.POST.get('producto_id')
                del carrito[producto_id]
                request.session['carrito'] = carrito
                print("entro")
                # Eliminar el producto de la tabla ProductosPedido
                ProductosPedido.objects.filter(pedido=pedido, producto_id=producto_id).delete()
                
                total_productos_actualizado = sum(int(item['total_producto']) for item in carrito.values())
                iva_actualizado = total_productos_actualizado * 0.19
                total_actualizado = round(total_productos_actualizado + iva_actualizado)
                return JsonResponse({'success': True, 'total_actualizado': numberWithPoints(total_actualizado)})
            elif 'notaDespacho' in request.POST:
                notaPedido = request.POST.get('notaPedido')
                pedido.notaDespachador = notaPedido.strip()
                pedido.save()

        elif user.tipo_usuario_id == 4 or user.tipo_usuario in adminIds: #Facturadores
            if 'confirmarFacturacion' in request.POST:
                if not pedido.estado_id >= 3:
                    pedido.estado_id = 3
                    pedido.facturado_por = user
                    pedido.facturado_hora = timezone.now()
                    pedido.actualizar_dinero_generado_cliente()
                    pedido.save()
                else:
                    issue = ERROR_17
      
        elif user.tipo_usuario_id == 5 or user.tipo_usuario in adminIds: # Asignadores
            if 'confirmarRepartidor' in request.POST:
                form = SeleccionarRepartidor(request.POST)
                if not pedido.estado_id >= 4:
                    if form.is_valid():
                        pedido.estado_id = 4
                        pedido.asignador_reparto = user
                        pedido.asignacion_hora = timezone.now()
                        pedido.repartido_por = get_object_or_404(Usuarios, pk=request.POST.get('repartidor'))
                        pedido.save()
                    else:
                        return render(request, HTMLORDERDETAIL,{
                            'success': False,
                            'msg': ERROR_2
                        }) 
                else:
                    issue = ERROR_19
            elif 'modificarRepartidor' in request.POST:
                form = SeleccionarRepartidor(request.POST)
                if form.is_valid():
                    pedido.asignacion_hora = timezone.now()
                    pedido.repartido_por = get_object_or_404(Usuarios, pk=request.POST.get('repartidor'))
                    pedido.save()
                    
            else:
                return render(request,HTMLORDERDETAIL,{
                    'success':False,
                    'msg': ERROR_13
                })
        else:
            return render(request, HTMLORDERDETAIL, {
                'success': False,
                'msg': ERROR_13
            })
         
    #GET   
    pedido = get_object_or_404(Pedido, pk=order)
    cliente = get_object_or_404(Clientes, pk=pedido.cliente_id)
    productos = ProductosPedido.objects.filter(pedido_id=order)
    print(productos)
    if user.tipo_usuario_id == 2:
        if pedido.vendedor_id == user.id:
            return render(request, HTMLORDERDETAIL, {
                'success': True,
                'pedido': pedido,
                'user': user,
                'cliente': cliente,
                'productos': productos
            })
        else:
            return render(request, HTMLORDERDETAIL, {
                'success': False,
                'msg': ERROR_13
            })
    elif user.tipo_usuario_id == 3: #Despachadores
        despachadores_activos = None
        puede_ayudar = False
        if pedido.estado_id == 1:
            despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido) 
            puede_ayudar = not despachadores_activos.filter(despachador_id=user.id).exists()
        elif pedido.estado_id == 2:
            despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido) 
            print(despachadores_activos)
            
        return render(request, HTMLORDERDETAIL, {
            'success': True,
            'pedido': pedido,
            'user': user,
            'cliente': cliente,
            'productos': productos,
            'despachadoresActivos': despachadores_activos,
            'puede_ayudar': puede_ayudar,
            'issue3': issue
        })
    elif user.tipo_usuario_id == 4:
        pedido = get_object_or_404(Pedido, pk=order)
        despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido) 
        return render(request, HTMLORDERDETAIL, {
                'success': True,
                'pedido': pedido,
                'cliente': cliente,
                'productos': productos,
                'user': user,
                'despachadoresActivos': despachadores_activos,
                'issue4': issue
            })
    elif user.tipo_usuario_id == 5: #Asignador
        pedido = get_object_or_404(Pedido, pk=order)
        despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido) 
        
        return render(request,HTMLORDERDETAIL, {
            'success': True,
            'pedido': pedido,
            'cliente': cliente,
            'productos': productos,
            'user': user,
            'form': SeleccionarRepartidor(),
            'despachadoresActivos': despachadores_activos,
            'issue5': issue
        })

    return render(request, HTMLORDERDETAIL, {
        'success': False,
        'msg': ERROR_13
    })

@login_required
def Orders(request, filtered=None):
    user = get_object_or_404(Usuarios, pk=request.user.id)
    PEDIDOS_POR_PAGINA = 10
    history=False
    pedidos = []

    if not filtered:
        if user.tipo_usuario_id == 2:  # Vendedor
            pedidos = Pedido.objects.filter(vendedor=user.id).order_by('-id')
        elif user.tipo_usuario_id == 3: #Despachador
            pedidos = Pedido.objects.filter(estado_id__in=[0, 1]).order_by('-id')
        elif user.tipo_usuario_id == 4:
            pedidos = Pedido.objects.filter(estado_id=2).order_by('-id')
        elif user.tipo_usuario_id == 5:
            pedidos = Pedido.objects.filter(estado_id=3).order_by('-id')


    elif filtered == "historial": 
        history=True
        if user.tipo_usuario_id == 3:  # Despachador
            handler_despachos = HandlerDespacho.objects.filter(despachador=user)
            pedidos = [handler_despacho.pedido for handler_despacho in handler_despachos]
            pedidos = sorted(pedidos, key=lambda x: x.id, reverse=True)
        elif user.tipo_usuario_id == 4:
            pedidos = Pedido.objects.filter(facturado_por=user.id)
        elif user.tipo_usuario_id == 5:
            pedidos = Pedido.objects.filter(asignador_reparto_id=user.id)
   

    paginator = Paginator(pedidos, PEDIDOS_POR_PAGINA)
    page_number = request.GET.get('page', 1)

    try:
        pedidos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        pedidos_paginados = paginator.page(1)
    except EmptyPage:
        pedidos_paginados = paginator.page(paginator.num_pages)

    return render(request, HTMLORDERS, {'pedidos': pedidos_paginados,
                                        'user': user,
                                        'history': history})


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
                return render(request, HTMLHOME, {'form': recycledForm,'error': ERROR_6})        
            logedUser = authenticate(request, username=documento, password=password)
            
            #Verificar que el usuario exista y su contraseña sea correcta
            if logedUser is None:
                recycledForm = InicioSesionForm(initial={'documento': documento})
                return render(request, HTMLHOME, {'form': recycledForm,'error':ERROR_4})
            
            login(request, logedUser)
            userType = logedUser.tipo_usuario_id
            if userType in [0,1,2,3,4,5]:
                return redirect(reverse('registro')) 
            else:
                logout(request)
                return render(request, HTMLHOME, {'form': newForm,'error': ERROR_5})
        else:
            return render(request, HTMLHOME,{'form':newForm, 'error': ERROR_2})
    return render(request, HTMLHOME, {'form': newForm})

@login_required
def Logout(request):
    logout(request)
    return redirect(reverse('home'))

def Registro(request):
    newForm = RegistroUsuariosForm()
    #Post
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
                event = None
                documento = form.cleaned_data['username']
                password = form.cleaned_data['password']
                tipo_usuario = form.cleaned_data['tipo_usuario']
                
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
                #Desactivar el acceso si el usuario es tipo repartidor
                user.is_active = tipo_usuario.id != TIPOREPARTIDOR
                event = EXITO_4 if not user.is_active else EXITO_1
                user.save()
                
                return render(request, HTMLREGISTRO, {
                    "form": newForm,
                    "evento": event,
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
    
    data = {
            'productos':carrito,
            'total_productos': numberWithPoints(total_productos),
            'iva': numberWithPoints(iva),
            'total_venta':numberWithPoints(total_productos+iva),
            'cantidad_productos': len(carrito),
            'form': form,
            'event': '',
            'success':False,
            }
    
    if "confirmar_venta" in request.POST:
        cliente = request.POST.get('cliente')
        pedido_nota = request.POST.get('nota')
        productos_dict = request.POST.get('productos')
        try:
            productos_dict = json.loads(productos_dict)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'msg': "JSON no válido"})
        
        if not cliente:
            return JsonResponse({'success': False, 'msg': "Por favor escoja un cliente."})
        elif not productos_dict:
            return JsonResponse({'success': False, 'msg': "No hay productos en el pedido."})
        else:
            cliente = get_object_or_404(Clientes, pk=cliente)   
            estado = get_object_or_404(Estados, pk=0)
            #Actualizar carrito mientras se comrpueba la existencia de los productos solicitados
            for producto_id, cantidad in productos_dict.items():
                if producto_id in carrito:
                    producto_real = get_object_or_404(Producto, pk=producto_id)
                    carrito[producto_id] = {
                        'precio': producto_real.precio,
                        'cantidad_existencias': producto_real.cantidad,
                        'cantidad': cantidad,
                        'total_producto': int(cantidad) * int(producto_real.precio)
                    }
                else: 
                    return JsonResponse({'success': False, 'msg': "Hay productos que no existen"})

            #Construir pedido
            nuevo_pedido = Pedido(
                vendedor=request.user,
                cliente=cliente,
                estado=estado,
                direccion=cliente.direccion,
                valor=getCartPrice(request) + getCartPrice(request)*0.19,
                nota=pedido_nota
            )
            nuevo_pedido.save()
            
            #Añadir productos al pedido
            for producto_id, cantidad in productos_dict.items():
                verificar_producto = get_object_or_404(Producto, pk=producto_id)
                producto_pedido = ProductosPedido(
                    producto = verificar_producto,
                    pedido = nuevo_pedido,
                    cantidad=cantidad
                )
                producto_pedido.save()
            
            #Limpiar carrito despues de una operacion exitosa
            carrito.clear()
            request.session['carrito'] = carrito
            return JsonResponse({'success': True, 'msg': 'Venta completada'})
    
    elif "crear_cliente" in request.POST:
        nombre = request.POST.get('nombre_cli').strip()
        direccion = request.POST.get('direccion_cli').strip()
        
        if nombre and direccion:
            nuevo_cliente = Clientes(nombre=nombre, direccion=direccion)
            nuevo_cliente.save()
            return render(request, HTMLCARRITO, data)
        else:
            data['event'] = "Nombre o direccion inválida"
            return render(request, HTMLCARRITO, data)
    
    return render(request, HTMLCARRITO, data)
    