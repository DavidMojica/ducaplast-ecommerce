from django.shortcuts import render
from .forms import registroUsuariosForm
# Create your views here.
def Home(request):
    return render(request, "home.html")

def Registro(request):
    return(render(request, "registro.html", {
        'form': registroUsuariosForm
    }))
