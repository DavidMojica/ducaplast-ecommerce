from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import registroUsuariosForm, inicioSesionForm


# Variables

#Arrays - listas
adminIds = [0, 1]

#Notificaciones
EXITO_1 = "El usuario ha sido creado correctamente."
ERROR_1 = "El documento que intentó ingresar, ya existe."
ERROR_2 = "Formulario inválido."
ERROR_3 = "Error desconocido."
ERROR_4 = "Usuario o contraseña incorrecta."
ERROR_5 = "Este usuario no pudo ser redireccionado. Comunique este error."
ERROR_6 = "Usuario o documento demasiado corto(s)."
#-----------Functions----------#
def stripForm(form):
    for campo in form.fields:
        if isinstance(form.cleaned_data[campo], str):
            form.cleaned_data[campo] = form.cleaned_data[campo].strip()
    return form 


# Create your views here.
def Home(request):
    newForm = inicioSesionForm()
    if request.method == 'POST':
        form = inicioSesionForm(request.POST)
        if form.is_valid():
            form = stripForm(form)
            
            documento = form.cleaned_data['documento']
            password = form.cleaned_data['password']
            
            #Verificar el minimo de carácteres para cada campo
            if len(documento) < 6 or len(password) < 8:
                recycledForm = inicioSesionForm(initial={'documento': documento})
                return render(request, "home.html", {'form': recycledForm,
                                                     'error': ERROR_6})
            
            logedUser = authenticate(request, username=documento, password=password)
            
            #Verificar que el usuario exista y su contraseña sea correcta
            if logedUser is None:
                recycledForm = inicioSesionForm(initial={'documento': documento})
                return render(request, "home.html", {'form': recycledForm,
                                                    'error':ERROR_4})
            else:
                login(request, logedUser)
                userType = logedUser.tipo_usuario
                if userType == '10':
                    return redirect()
                elif userType == '11':
                    return redirect()
                elif userType == '12':
                    return redirect()
                elif userType == '13':
                    return redirect()
                elif userType == '14':
                    return redirect()
                else:
                    logout(request)
                    return render(request, "home.html", {'form': newForm,
                                                         'error': ERROR_5})
        else:
            return render(request, "home.html",{'form':newForm,
                                                'error': ERROR_2})
    return render(request, "home.html", {'form': newForm})

       
    
    

def Registro(request):
    newForm = registroUsuariosForm()
    if request.method == "POST":
        form = registroUsuariosForm(request.POST)
        #Verificar que el documento no se haya registrado antes.
        if form.has_error("username", code="unique"):
            return render(request, "registro.html", {
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
                user = form.save(commit=False)
                user.username = form.cleaned_data['username']
                user.set_password(form.cleaned_data['password'])
                user.email = form.cleaned_data['email']
                user.save()
                
                return render(request, "registro.html", {
                    "form": newForm,
                    "evento": EXITO_1,
                    "exito": True,
                    "documento": f"Usuario login: {form.cleaned_data['username']}",
                    "password": f"Contraseña: {form.cleaned_data['password']}"
                })
            except Exception as e:
                return render(request, "registro.html", {
                    "form": form,
                    "evento": ERROR_3,
                    "exito": False,
                })
        else:
            return render(request, "registro.html", {
                    "form": form,
                    "evento": ERROR_2,
                    "exito": False,
                })
    #GET
    return render(request, "registro.html", {'form': newForm })