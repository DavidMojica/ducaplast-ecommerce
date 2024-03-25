import random
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models.functions import Cast
from django.db.models import FloatField, Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import FiltrarUsuarios,ModificarCliente, FiltrarCliente,FiltrarRecibos, ProductoForm, RegistroUsuariosForm, InicioSesionForm, FiltrarProductos, DetallesPedido, SeleccionarRepartidor, TipoUsuario
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
HTMLUSERS = "users.html"
HTMLUSERDETAIL = "user_detail.html"
HTMLPRODUCTOS = "productos.html"
HTMLPRODUCTODETAIL = "product_detail.html"
HTMLPRODUCTOADD = "product_add.html"
HTMLCHARTS = "charts.html"
HTMLCLIENTES = "clientes.html"
HTMLCLIENTEDETAIL = "client_detail.html"
HTMLCLIENTEADD = "client_add.html"

#Notificaciones
SUCCESS_1 = "El usuario ha sido creado correctamente."
SUCCESS_2 = "Sus datos fueron actualizados correctamente"
SUCCESS_3 = "Contraseña actualizada correctamente"
SUCCESS_4 = "El usuario se ha creado correctamente, pero como es repartidor no tiene acceso al sistema todavía."
SUCCESS_5 = "El repartidor se actualizó correctamente"
SUCCESS_6 = "Se ha suspendido al usuario correctamente"
SUCCESS_7 = "Se ha removido la suspensión correctamente"
SUCCESS_8 = "No se puede quitar la suspensión a los repartidores porque no se les ha concedido la entrada a la plataforma todavía."
SUCCESS_9 = "Se ha borrado un usuario correctamente"
SUCCESS_10 = "Se ha creado el cliente correctamente"
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
ERROR_20 = "JSON no válido"
ERROR_21 = "No hay productos en el pedido."
ERROR_22 = 'El nombre del cliente ya está registrado.'

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
            return redirect('orders')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

#Obtener el precio de los articulos del carro y actualizar sus respectivos valores con puntos decimales.
@login_required
def getCartPrice(request):
    carrito = request.session.get('carritoVenta', {})
    total_productos = 0
    if carrito:
        for key, producto in carrito.items():
            total_productos += int(producto['precio']) * int(producto['cantidad'])
            producto['precio_str'] = numberWithPoints(producto['precio'])
            producto['total_producto_str'] = numberWithPoints(producto['total_producto'])
        return total_productos
    
#Devuelve el precio actualizado con el IVA
@login_required
def calcular_total_actualizado(request):
    carrito = request.session.get('carrito', {})
    total_productos_actualizado = sum(int(item['total_producto']) for item in carrito.values())
    iva_actualizado = total_productos_actualizado * 0.19
    total_actualizado = round(total_productos_actualizado + iva_actualizado)
    return total_actualizado

@login_required
def ayudarEnDespacho(request, user, pedido):
    handler = HandlerDespacho(despachador = user, pedido = pedido)
    handler.save()
  
def getPuedeAyudar(pedido, despachadores_activos, user):
    if pedido.estado_id in [1, 2]:
        return not despachadores_activos.filter(despachador_id=user.id).exists()
    return False  

def loadCart(request, pedido, initial=True):
    carrito = {}
    productos = ProductosPedido.objects.filter(pedido_id=pedido)

    for producto_pedido in productos:
        producto_real = get_object_or_404(Producto, pk=producto_pedido.producto.id)
        carrito[producto_pedido.producto_id] = {
            'precio': producto_real.precio,
            'cantidad_existencias': producto_real.cantidad,
            'cantidad': producto_pedido.cantidad,
            'total_producto': int(producto_pedido.cantidad) * int(producto_real.precio)
        }
    request.session['carrito'] = carrito
    if not initial:
        pedido.valor = calcular_total_actualizado(request)
        pedido.save()
    return carrito

def updateCart(request, pedido, productos_modificados):
    carrito = {}
    productos_en_pedido = ProductosPedido.objects.filter(pedido=pedido)
    for producto_id, cantidad in productos_modificados.items():
        producto_real = get_object_or_404(Producto, pk=producto_id)
        carrito[int(producto_id)] = {
            'precio': producto_real.precio,
            'cantidad_existencias': producto_real.cantidad,
            'cantidad': cantidad,
            'total_producto': int(cantidad) * int(producto_real.precio)
        }
        producto_en_pedido = productos_en_pedido.get(producto=producto_real)
        producto_en_pedido.cantidad = cantidad
        producto_en_pedido.total_producto = int(cantidad) * producto_real.precio
        producto_en_pedido.save()
    request.session['carrito'] = carrito
    pedido.valor = calcular_total_actualizado(request)
    pedido.save()
    return carrito

def filtrar_productos(request):
    form = FiltrarProductos(request.GET)
    productos = Producto.objects.order_by('id')
    
    if form.is_valid():
        id_producto = form.cleaned_data.get('id')
        nombre = form.cleaned_data.get('nombre')
        ordenar = form.cleaned_data.get('ordenar')
        disponibles = form.cleaned_data.get('disponibles')
        
        # Extraer los datos
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
        
        # Filtrar los datos
        if id_producto:
            productos = productos.filter(id=id_producto)
           
        if nombre:
            productos = productos.filter(descripcion__icontains=nombre)
        
        # Modulo disponibles
        if disponibles:
            productos = productos.filter(cantidad__gt=0)
    
    return productos
#-----------------------------------------------------------------------#
#-----------------------------------Views-------------------------------#
#-----------------------------------------------------------------------#
@login_required
def ClientAdd(request):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        newForm = ModificarCliente()
        data = {'form': newForm,
                'bgevent': 'bg-danger'}
        
        if request.method == 'POST':
            form = ModificarCliente(request.POST)
            if form.is_valid():
                nombre = form.cleaned_data.get('nombre')
                direccion = form.cleaned_data.get('direccion')
                
                # Verificar si ya existe un cliente con el mismo nombre
                if Clientes.objects.filter(nombre=nombre).exists():
                    data['msg'] = ERROR_22
                    data['form'] = form
                else:
                    nuevo_cliente = Clientes(
                        nombre=nombre,
                        direccion=direccion
                    )
                    nuevo_cliente.save()
                    data['msg'] = SUCCESS_10
                    data['bgevent'] = 'bg-success'
            else:
                data['msg'] = ERROR_2
        
        return render(request, HTMLCLIENTEADD, {**data})
    else:
        return redirect('orders')

@login_required
def ClientDetail(request, clientid=None):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        cliente = get_object_or_404(Clientes, pk=clientid)
        if request.method == 'POST':
            form = ModificarCliente(request.POST)
            if form.is_valid():
                nombre = form.cleaned_data.get('nombre')
                direccion = form.cleaned_data.get('direccion')
                cliente.nombre = nombre
                cliente.direccion = direccion
                cliente.save()
                return redirect('clientes')
        else:
            form = ModificarCliente(initial={'nombre': cliente.nombre, 'direccion': cliente.direccion})

        return render(request, 'client_detail.html', {'form': form, 'cliente': cliente})
    else:
        return redirect('orders')
    
#super -- TEST N/S
@login_required
def ClientesView(request):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        form = FiltrarCliente(request.GET)
        CLIENTES_POR_PAGINA = 15
        data = {'form':form}
        clientes = Clientes.objects.all()
        
        if form.is_valid():
            id = form.cleaned_data.get('id')
            nombre = form.cleaned_data.get('nombre')
            
            if id:
                clientes = clientes.filter(id=id)
            if nombre:
                clientes = clientes.filter(nombre__icontains=nombre)
                
        paginator = Paginator(clientes, CLIENTES_POR_PAGINA)
        page_number = request.GET.get('page')
        try:
            clientes_paginados = paginator.page(page_number)
        except PageNotAnInteger:
            clientes_paginados = paginator.page(1)
        except EmptyPage:
            clientes_paginados = paginator.page(paginator.num_pages)
            
        return render(request, HTMLCLIENTES, {**data, 'clientes':clientes_paginados})
    else:
        return redirect('orders')
    
#super -- TEST N/S
@login_required
def Charts(request):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        data = {}   
        return render(request, HTMLCHARTS, {**data})
    else:
        return redirect('orders')

#super -- TEST N/S
@login_required
def ProductDetails(request, productid=None):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        producto = Producto.objects.get(pk=productid)
        if request.method == 'POST':
            form = ProductoForm(request.POST, instance=producto)
            if form.is_valid():
                form.save()
                return redirect('productos') # Redirecciona a la vista de productos
        else:
            form = ProductoForm(instance=producto)
        return render(request, HTMLPRODUCTODETAIL, {'form': form})
    else:
        return redirect('orders')

#super -TEST N/S
@login_required
def ProductAdd(request):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        if request.method == 'POST':
            form = ProductoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('productos') # Redirecciona a la vista de productos
        else:
            form = ProductoForm()
        return render(request, HTMLPRODUCTOADD, {'form':form})
    else:
        return redirect('orders')

#Super -TEST N/S
@login_required
def Productos(request):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        PRODUCTOS_POR_PAGINA = 18
        form = FiltrarProductos(request.GET)
        productos = filtrar_productos(request)
        paginator = Paginator(productos, PRODUCTOS_POR_PAGINA)
        page_number = request.GET.get('page')
        
        #Post
        if request.method == 'POST':
            if 'borrar_producto' in request.POST:
                id = request.POST.get('productoid')
                producto = get_object_or_404(Producto, pk=id)
                producto.delete()

        try:
            productos_paginados = paginator.page(page_number)
        except PageNotAnInteger:
            productos_paginados = paginator.page(1)
        except EmptyPage:
            productos_paginados = paginator.page(paginator.num_pages)
        data = {'form': form, 'productos': productos_paginados}
        return render(request, HTMLPRODUCTOS, {**data})
    else:
        return redirect('orders')

#Super -TEST N/S
@login_required
def UserDetail(request, userid):
    user_to_modify = get_object_or_404(Usuarios, pk=userid)
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        tipos_usuario = TipoUsuario.objects.all()
        data = {'user_modify': user_to_modify,
                'request_user': request.user,
                'tipos_usuario':tipos_usuario}
        #POST
        if request.method == 'POST':
            if 'reestablecer' in request.POST:  
                nuevaContrasena = str(random.randint(10000000, 99999999))
                user_to_modify.set_password(nuevaContrasena)
                user_to_modify.save()
                data['password_changed'] = nuevaContrasena
                
            elif 'acc_data' in request.POST:
                nombre = request.POST.get('nombre').strip()
                apellidos = request.POST.get('apellidos').strip()
                email = request.POST.get('email').strip()
                tipo_usuario = request.POST.get('tipo_usuario')
                
                tipo_instance = get_object_or_404(TipoUsuario, pk=tipo_usuario)
                user_to_modify.first_name = nombre
                user_to_modify.last_name = apellidos
                user_to_modify.email = email
                user_to_modify.tipo_usuario = tipo_instance
                user_to_modify.save()
                
        return render(request, HTMLUSERDETAIL, {**data})
    else:
        return redirect('orders')

#super - TEST N/S
@login_required
def Users(request):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
        msg = ""
        form = FiltrarUsuarios(request.GET)
        USUARIOS_POR_PAGINA = 20
        usuarios = Usuarios.objects.all().order_by('id')
        data = {'form': form}
        
        #POST
        if request.method == 'POST':
            userid = request.POST.get('userid')
            user = get_object_or_404(Usuarios, pk=userid)
            if 'suspender_usuario' in request.POST:
                user.is_active = False
                msg = SUCCESS_6
                altype = 'info'
                user.save()
            elif 'readmitir_usuario' in request.POST:
                if not user.tipo_usuario_id == 6:
                    user.is_active = True
                    msg = SUCCESS_7
                    altype = 'info'
                    user.save()
                else:
                    msg = SUCCESS_8
                    altype = 'danger'
                    
            elif 'borrar_usuario' in request.POST:
                user.delete()
                msg = SUCCESS_9
                altype = 'danger'
            
            data['msg'] = msg
            data['type'] = altype
                
        #GET
        #Filtro?
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre').lower()
            id = form.cleaned_data.get('id')
            tipo_usuario = form.cleaned_data.get('tipo_usuario')
            
            if nombre:
                usuarios = form.buscar_usuarios_por_nombre()
            if tipo_usuario:
                usuarios = usuarios.filter(tipo_usuario=tipo_usuario)
            if id:
                usuarios = usuarios.filter(id=id)
            
        #Paginador
        paginator = Paginator(usuarios, USUARIOS_POR_PAGINA)
        page_number = request.GET.get('page')
        
        try:
            usuarios_paginados = paginator.page(page_number)
        except PageNotAnInteger:
            usuarios_paginados = paginator.page(1)
        except EmptyPage:
            usuarios_paginados = paginator.page(paginator.num_pages)
            
        return render(request, HTMLUSERS, {**data, 'users': usuarios_paginados})
    else:
        return redirect('orders')

# N/S
@login_required
def OrderDetail(request, order):
    user = get_object_or_404(Usuarios, pk=request.user.id)
    issue = ""
    pedido = get_object_or_404(Pedido, pk=order)
    cliente = get_object_or_404(Clientes, pk=pedido.cliente_id)
    productos = ProductosPedido.objects.filter(pedido_id=order)
    despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido)
    carrito = loadCart(request, pedido)
    
    #Post
    if request.method == 'POST':
        #----------------TAREAS DE DESPACHO, ESTADO 0 PARA 1----------------#
        if user.tipo_usuario_id == 3 or user.tipo_usuario_id in adminIds and pedido.estado_id in [0,1]: #Despachadores
            if "confirmar_despacho" in request.POST:
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
                request.session['carrito'] = carrito
                despachadores_activos = HandlerDespacho.objects.filter(pedido=pedido) 
                if not pedido.estado_id >= 2:
                    if despachadores_activos.filter(despachador_id=user.id).exists():
                        total_actualizado = calcular_total_actualizado(request)
                        pedido.estado_id = 2
                        pedido.valor = total_actualizado
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
                    return JsonResponse({'success': False, 'msg': ERROR_20})
                
                if not productosModificados:
                    return JsonResponse({'success': False, 'msg': ERROR_21})
                
                carrito = updateCart(request,pedido,productosModificados)
                total_actualizado = calcular_total_actualizado(request)
                return JsonResponse({'success': True, 'total_actualizado': numberWithPoints(total_actualizado)})
            elif 'borrarProducto' in request.POST:
                producto_id = int(request.POST.get('producto_id'))
                ProductosPedido.objects.filter(pedido=pedido, producto_id=producto_id).delete()
                carrito = loadCart(request, pedido, False)
                total_actualizado = calcular_total_actualizado(request)  
            elif 'notaDespacho' in request.POST:
                notaPedido = request.POST.get('notaPedido')
                pedido.notaDespachador = notaPedido.strip()
                pedido.save()
                
        #----------------TAREAS DE FACTURACIÓN, ESTADO 2----------------#
        elif user.tipo_usuario_id == 4 or user.tipo_usuario_id in adminIds and pedido.estado_id == 2: #Facturadores
            if 'confirmarFacturacion' in request.POST:
                if not pedido.estado_id >= 3:
                    pedido.estado_id = 3
                    pedido.facturado_por = user
                    pedido.facturado_hora = timezone.now()
                    pedido.save()
                else:
                    issue = ERROR_17

        #----------------TAREAS DE ASIGNACION, ESTADO 3----------------#
        elif user.tipo_usuario_id == 5 or user.tipo_usuario_id in adminIds and pedido.estado_id == 3: # Asignadores
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
        #----------------TAREAS DE COMPLETACIÓN, ESTADO 4 PARA 5----------------#
        elif user.tipo_usuario_id in adminIds and pedido.estado_id == 4:
            if 'completarPedido' in request.POST:
                if not pedido.estado_id >= 5:
                    pedido.estado_id = 5
                    pedido.actualizar_dinero_generado_cliente()
                    pedido.completado_por = user
                    pedido.completado_hora = timezone.now()
                    pedido.save()
        else:
            return render(request, HTMLORDERDETAIL, {
                'success': False,
                'msg': ERROR_13
            })
         
    #GET   
    data = {
        'success': True,
        'pedido': pedido,
        'cliente': cliente,
        'productos': productos,
        'user': user,
        'despachadoresActivos': despachadores_activos,
        'isAdmin': False
    }
        
    if user.tipo_usuario_id in adminIds: #Gerente - administrador
        data['isAdmin'] = True
        data['puede_ayudar'] = getPuedeAyudar(pedido, despachadores_activos, user)
        form = SeleccionarRepartidor() if pedido.estado_id == 3 or 4 else None
        return render(request, HTMLORDERDETAIL, {**data, 'form':form})
    elif user.tipo_usuario_id == 2:
        return render(request, HTMLORDERDETAIL, {**data}) if pedido.vendedor_id == user.id else render(request, HTMLORDERDETAIL, {'success': False, 'msg': ERROR_13})
    elif user.tipo_usuario_id == 3: #Despachadores
        data['puede_ayudar'] = getPuedeAyudar(pedido, despachadores_activos, user)
        return render(request, HTMLORDERDETAIL, {**data, 'issue3':issue})
    elif user.tipo_usuario_id in [4,5]: #Facturadores - asignadores
        form = SeleccionarRepartidor() if user.tipo_usuario_id == 5 else None
        issue_key = 'issue5' if user.tipo_usuario_id == 5 else 'issue4'
        return render(request, HTMLORDERDETAIL, {**data, 'form': SeleccionarRepartidor(), issue_key: issue})

#N/S
@login_required 
def Orders(request, filtered=None):
    user = get_object_or_404(Usuarios, pk=request.user.id)
    form = FiltrarRecibos(request.GET)
    PEDIDOS_POR_PAGINA = 10
    pedidos = []
    data= {'user': user, 'history': False, 'form':form}

    if not filtered:
        if user.tipo_usuario_id in adminIds:
            pedidos = Pedido.objects.exclude(estado_id=5).order_by('-fecha')
        elif user.tipo_usuario_id == 2:  # Vendedor
            pedidos = Pedido.objects.filter(vendedor=user.id).order_by('-fecha')
        elif user.tipo_usuario_id == 3: #Despachador
            pedidos = Pedido.objects.filter(estado_id__in=[0, 1]).order_by('-fecha')
        elif user.tipo_usuario_id == 4: #Facturador
            pedidos = Pedido.objects.filter(estado_id=2).order_by('-fecha')
        elif user.tipo_usuario_id == 5: #Asignador
            pedidos = Pedido.objects.filter(estado_id=3).order_by('-fecha')

    elif filtered == "historial": 
        data['history'] = True
        if user.tipo_usuario_id in adminIds:
            pedidos = Pedido.objects.filter(estado_id=5).order_by('-fecha')
            if form.is_valid():
                id = form.cleaned_data.get('id')
                vendedor = form.cleaned_data.get('vendedor')
                cliente = form.cleaned_data.get('cliente')
                fecha = form.cleaned_data.get('fecha')
                completado_fecha = form.cleaned_data.get('completado_fecha')
                if id:
                    pedidos = pedidos.filter(id=id)
                if vendedor:
                    pedidos = pedidos.filter(vendedor=vendedor)
                if cliente:
                    pedidos = pedidos.filter(cliente=cliente)
                if fecha:
                    pedidos = pedidos.filter(fecha__date=fecha)
                if completado_fecha:
                    pedidos = pedidos.filter(completado_hora__date=completado_fecha)

        elif user.tipo_usuario_id == 3:  # Despachador
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
    return render(request, HTMLORDERS, {**data, 'pedidos': pedidos_paginados})

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
                return redirect(reverse('orders')) 
            else:
                logout(request)
                return render(request, HTMLHOME, {'form': newForm,'error': ERROR_5})
        else:
            return render(request, HTMLHOME,{'form':newForm, 'error': ERROR_2})
    return render(request, HTMLHOME, {'form': newForm})
#N/A
@login_required
def Logout(request):
    logout(request)
    return redirect(reverse('home'))

#N/S - 
@login_required
def Registro(request):
    req_user = get_object_or_404(Usuarios, pk=request.user.id)
    if req_user.tipo_usuario_id in adminIds:
    
        newForm = RegistroUsuariosForm()
        data = {'form': newForm, 'exito': False}
        #Post
        if request.method == "POST":
            form = RegistroUsuariosForm(request.POST)
            data['form'] = form
            #Verificar que el documento no se haya registrado antes.
            if form.has_error("username", code="unique"):
                data['evento'] = ERROR_1
                return render(request, HTMLREGISTRO, {**data})
            
            #Verificar la validez del formulario (campos en blanco, tipos de datos correctos)
            if form.is_valid():
                form = stripForm(form)
                try:
                    event = None
                    documento = form.cleaned_data['username']
                    password = form.cleaned_data['password']
                    tipo_usuario = form.cleaned_data['tipo_usuario']
                    
                    if len(documento) < DOCLENGTHMIN or len(password) < PASSLENGTHMIN:
                        data['evento'] = ERROR_1
                        return render(request, HTMLREGISTRO, {**data})
                    
                    user = form.save(commit=False)
                    user.username = documento
                    user.set_password(password)
                    user.email = form.cleaned_data['email']
                    #Desactivar el acceso si el usuario es tipo repartidor
                    user.is_active = tipo_usuario.id != TIPOREPARTIDOR
                    event = SUCCESS_4 if not user.is_active else SUCCESS_1
                    user.save()
                    
                    data['documento'] = f"Usuario login: {documento}"
                    data['password']  = f"Contraseña: {form.cleaned_data['password']}"
                    data['evento']    = event
                    data['exito']     = True
                    data['form']      = newForm
                    return render(request, HTMLREGISTRO, {**data})
                except Exception as e:
                    data['evento'] = ERROR_3
                    return render(request, HTMLREGISTRO, {**data})
            else:
                data['evento'] = ERROR_2
                return render(request, HTMLREGISTRO, {**data})
        #GET
        return render(request, HTMLREGISTRO, {**data})
    else:
        return redirect('orders')
#N/S
@login_required
def EditarCuenta(request):
    user = get_object_or_404(Usuarios, pk=str(request.user.id))
    if request.method == "POST":
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
            return render(request, HTMLEDITARCUENTA, {"account_data_event": SUCCESS_2})
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
#N/N
@login_required
def CartHandler(request):
    carrito = request.session.get('carritoVenta', {})
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
                request.session['carritoVenta'] = carrito
                return JsonResponse({'success': True, 'event': event,})
            except Producto.DoesNotExist:
                event = "El producto no existe"
              
        #Borrar  
        elif action == "2":
            if producto_id in carrito:
                print(producto_id)
                del carrito[producto_id]
                event = "Producto borrado"
                carrito_vacio = len(carrito) == 0  
            total_productos_actualizado = sum(int(item['total_producto']) for item in carrito.values())
            iva_actualizado = total_productos_actualizado * 0.19
            total_actualizado = total_productos_actualizado + iva_actualizado
            request.session['carritoVenta'] = carrito
            return JsonResponse({'success': True, 'event': event, 'total_productos': numberWithPoints(total_productos_actualizado),
                                'iva': numberWithPoints(iva_actualizado), 'total_actualizado': numberWithPoints(total_actualizado), 'carrito_vacio': carrito_vacio,
                                'productos_cantidad': len(request.session['carritoVenta'])})
        #borrar todo el carrito
        elif action == "3":
            carrito.clear()
            request.session['carritoVenta'] = carrito
            return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
 #N/A
@login_required
def Catalogo(request):
    form = FiltrarProductos(request.GET)
    productos = filtrar_productos(request)
    PRODUCTOS_POR_PAGINA = 18
    paginator = Paginator(productos, PRODUCTOS_POR_PAGINA)
    page_number = request.GET.get('page')
    
    try:
        productos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    data = {'productos': productos_paginados,
            'carrito': request.session.get('carritoVenta', {}),
            'form': form }
    return render(request, HTMLCATALOGO,{**data})
              
@login_required
def Cart(request):
    #Valor total de los productos
    form = DetallesPedido(request.POST)
    carrito = request.session.get('carritoVenta', {})
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
            return JsonResponse({'success': False, 'msg': ERROR_20})
        
        if not cliente:
            return JsonResponse({'success': False, 'msg': "Por favor escoja un cliente."})
        elif not productos_dict:
            return JsonResponse({'success': False, 'msg': ERROR_21})
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
            request.session['carritoVenta'] = carrito
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

#-----------------------------------------------------------------------#
#--------------------------API's de los gráficos------------------------#
#-----------------------------------------------------------------------#
#Chart1 - Clientes más frecuentes
def get_chart_1(_request):
    top_clientes_ventas = Clientes.objects.annotate(num_pedidos=Count('pedido')).order_by('-num_pedidos')[:8]
    data = []
    for cliente in top_clientes_ventas:
        data.append({'value':cliente.dinero_generado, 'name': f"{cliente.nombre} ID: {cliente.id}"})
        
    chart = {
        'title': {
            'text': 'Clientes más frecuentes',
            'subtext': "Top 8",
            'x': 'center',
        },
        'tooltip': {
            'show': True,
            'trigger': 'item',
            'triggerOn':'mousemove|click'
        },
        'legend': {
            'top': 'bottom'
        },
        'series': [
          {
            'name': 'Clientes más frecuentes',
                'type': 'pie',
                'radius': [40, 160],
                'center': ['50%', '50%'],
                'roseType': 'area',
                'itemStyle': {
                'borderRadius': 8
            },
            'data': data
          }
        ]
      }
    
    return JsonResponse(chart)

#Chart2 - Dias mas concurridos
def get_chart_2(_request):
    pedidos_semana = Pedido.objects.all()
    pedidos_por_dia = [0,0,0,0,0,0,0] 
    for pedido in pedidos_semana:
        dia_semana = pedido.fecha.weekday()
        pedidos_por_dia[dia_semana] += 1
    
    pos_max = pedidos_por_dia.index(max(pedidos_por_dia))
    pos_min = pedidos_por_dia.index(min(pedidos_por_dia))
    
    pedidos_por_dia[pos_max] = {
        'value': pedidos_por_dia[pos_max],
        'itemStyle': {
        'color': '#a90000'
        }
    }
    pedidos_por_dia[pos_min] = {
        'value': pedidos_por_dia[pos_min],
        'itemStyle': {
        'color': '#00913f'
        }
    }
    
    chart = {
      'title': {
        'text': 'Días más concurridos',
        'subtext': "Venta en los días de la semana",
        'x': 'center',
      },
      'tooltip': {
            'show': True,
            'trigger': 'axis',
            'triggerOn':'mousemove|click'
        },
        'xAxis': {
          'type': 'category',
          'data': ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        },
        'yAxis': {
          'type': 'value'
        },
        'series': [
          {
            'data': pedidos_por_dia,
            'type': 'bar',
            'showBackground': True,
            'backgroundStyle': {
            'color': 'rgba(180, 180, 180, 0.2)'
            }
          }
        ]
    }
    
    return JsonResponse(chart)

#Chart3 - Ingresos por mes
def get_chart_3(_request):
    anios = list(Pedido.objects.values_list('fecha__year', flat=True).distinct())
    data = []
    for año in anios:
        pedidos_año = Pedido.objects.filter(fecha__year=año)
        ingresos_por_mes = [0] * 12  
        for pedido in pedidos_año:
            mes_pedido = pedido.fecha.month
            monto_pedido = pedido.valor  
            ingresos_por_mes[mes_pedido - 1] += monto_pedido  
        data.append({
            'name': str(año),
            'type': 'line',
            'stack': str(año),
            'data': ingresos_por_mes
        })
    chart = {
            'title': {
                'text': 'Ingresos por mes',
                'subtext': 'Se generará un año nuevo cuando se detecte un pedido en dicho momento'
            },
            'tooltip': {
                'trigger': 'axis'
            },
            'legend': {
                'data': anios.sort(),
                'top': '5%', 'right': '5%'
            },
            'grid': {
                'left': '3%',
                'right': '4%',
                'bottom': '3%',
                'containLabel': True
            },
            'xAxis': {
                'type': 'category',
                'boundaryGap': False,
                'data': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            },
            'yAxis': {
                'type': 'value'
            },
            'series': data
        }
    
    return JsonResponse(chart, safe=False)

#Chart4 - Productos que más se venden
def get_chart_4(_request):
    top_productos = ProductosPedido.objects.values('producto__descripcion').annotate(total_vendido=Sum('cantidad')).order_by('-total_vendido')[:20]
    dataAxis = []
    data = []
    for producto_info in top_productos:
        producto = producto_info['producto__descripcion']
        total_vendido = producto_info['total_vendido']
        dataAxis.append(producto)
        data.append(total_vendido)
    yMax = max(data)
    dataShadow = []
    for i in range(len(data)):
        dataShadow.append(yMax)
    chart = {
            'title': {
                'text': 'Productos que más se venden',
                'subtext': 'Top 20 (Puede hacer zoom con la rueda del mouse)'
            },
            'xAxis': {
                'data': dataAxis,
                'axisLabel': {
                    'inside': True,
                    'textStyle': {
                        'color': '#000'
                    }
                },
                'axisTick': {
                    'show': False
                },
                'axisLine': {
                    'show': False
                },
                'z': 10
            },
            'yAxis': {
                'axisLine': {
                    'show': False
                },
                'axisTick': {
                    'show': False
                },
                'axisLabel': {
                    'textStyle': {
                        'color': '#000'
                    }
                }
            },
            'tooltip': {
                'trigger': 'axis'
            },
            'dataZoom': [
                {
                    'type': 'inside'
                }
            ],
            'series': [
                { 
                    'type': 'bar',
                    'itemStyle': {
                        'color': 'rgba(0,0,0,0.05)'
                    },
                    'barGap': '-100%',
                    'barCategoryGap': '40%',
                    'data': dataShadow,
                    'animation': True
                },
                {
                    'type': 'bar',
                    'itemStyle': {
                        'color': "#438bc7"
                    },
                    'emphasis': {
                        'itemStyle': {
                            'color': "#438bc7"
                        }
                    },
                    'data': data
                }
            ]
        }
    return JsonResponse(chart)
