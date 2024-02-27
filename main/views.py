from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import registroUsuariosForm, inicioSesionForm
from .models import Usuarios

import re

# Variables
NOMBRELENGTHMIN = 2
APELLIDOSLENGTHMIN = 3
DOCLENGTHMIN = 6 #Minimo de carácteres para el documento
PASSLENGTHMIN = 8 #Minimo de carácteres para la contraseña

EMAILREGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
#Arrays - listas
adminIds = [0, 1]

#HTTDOCS
HTMLEDITARCUENTA = "editar_cuenta.html"
HTMLHOME = "home.html"
HTMLREGISTRO = "registro.html"

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
def stripForm(form):
    for campo in form.fields:
        if isinstance(form.cleaned_data[campo], str):
            form.cleaned_data[campo] = form.cleaned_data[campo].strip()
    return form 

def isEmpty(elements):
    return any(len(element.strip()) == 0 for element in elements)

def isValidEmail(email):
    if re.match(EMAILREGEX, email):
        return True
    return False

def unloginRequired(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('registro')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def EditarCuenta(request):
    user = get_object_or_404(Usuarios, pk=str(request.user.id))
    if request.method == "POST":
        print("acc_data" in request.POST)
        print("name" in request.POST)
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

@unloginRequired
def Home(request):
    newForm = inicioSesionForm()
    if request.method == 'POST':
        form = inicioSesionForm(request.POST)
        if form.is_valid():
            form = stripForm(form)
            
            documento = form.cleaned_data['documento']
            password = form.cleaned_data['password']
            
            #Verificar el minimo de carácteres para cada campo
            if len(documento) < DOCLENGTHMIN or len(password) < PASSLENGTHMIN:
                recycledForm = inicioSesionForm(initial={'documento': documento})
                return render(request, HTMLHOME, {'form': recycledForm,
                                                     'error': ERROR_6})
            
            logedUser = authenticate(request, username=documento, password=password)
            
            #Verificar que el usuario exista y su contraseña sea correcta
            if logedUser is None:
                recycledForm = inicioSesionForm(initial={'documento': documento})
                return render(request, HTMLHOME, {'form': recycledForm,
                                                    'error':ERROR_4})
            else:
                login(request, logedUser)
                userType = logedUser.tipo_usuario_id
                print(f"-------------->usertype {userType}")
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
def Registro(request):
    newForm = registroUsuariosForm()
    if request.method == "POST":
        form = registroUsuariosForm(request.POST)
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
def Logout(request):
    logout(request)
    return redirect(reverse('home'))