"""
URL configuration for ducaplast project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Home, name="home"),
    path('registro/', views.Registro, name="registro"),
    path('logout/', views.Logout, name='logout'),
    path('editar_cuenta/', views.EditarCuenta, name='editar_cuenta'),
    path('catalogo/', views.Catalogo, name='catalogo'),
    path('addtocart/', views.AddToCart, name="addtocart"),
    path('cart/', views.Cart, name='cart')
    
]
