from django.db import IntegrityError
from django.shortcuts import render

from main.models import Usuarios
from .forms import registroUsuariosForm

# Variables

#Arrays - listas
adminIds = [0, 1]

#Notificaciones
EXITO_1 = "El usuario ha sido creado correctamente."
ERROR_1 = "El usuario que intentó crear ya existe."

# Create your views here.
def Home(request):
    return render(request, "home.html")

def Registro(request):
    if request.method == "POST":
        form = registroUsuariosForm(request.POST)
        if form.is_valid():
            #Quitar espacios al principio y al final de los campos de texto
            for campo in form.fields:
                if isinstance(form.cleaned_data[campo], str):
                    form.cleaned_data[campo] = form.cleaned_data[campo].strip()
            
            
            # instancia del modelo y asignacion de datos del formulario
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            usuario, creado = Usuarios.objects.get_or_create(documento=user.documento)
            
            if creado:
                usuario.tipo_usuario = user.tipo_usuario
                usuario.save()
                
                return render(request, "registro.html", {
                    "form": form,
                    "evento": EXITO_1,
                    "exito": True,
                    "documento": form.documento,
                    "password": form.password
                })
            else:
                return render(request, "registro.html", {
                    "form": form,
                    "evento": ERROR_1,
                    "exito": False,
                })

    #GET
    else:
        form = registroUsuariosForm()
        
    return(render(request, "registro.html", {'form': form }))
