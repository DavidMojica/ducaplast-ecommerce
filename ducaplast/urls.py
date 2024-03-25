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
    path('carthandler/', views.CartHandler, name="carthandler"),
    path('cart/', views.Cart, name='cart'),
    path('orders/',views.Orders, name="orders"),
    path('orders/<str:filtered>',views.Orders, name="filtered_orders"),
    path('order_detail/<int:order>/', views.OrderDetail, name="order_detail"),
    path('users/', views.Users, name="users"),
    path('user_detail/<int:userid>/', views.UserDetail, name="user_detail"),
    path('productos/', views.Productos, name ="productos"),
    path('product_detail/<int:productid>',views.ProductDetails, name="product_detail"),
    path('product_add/', views.ProductAdd, name="product_add"),
    path('charts/', views.Charts, name="charts"),
    path('clientes/', views.ClientesView, name="clientes"),
    path('client_detail/<int:clientid>', views.ClientDetail, name='client_detail'),
    #API's de los charts
    path('get_chart_1/', views.get_chart_1, name="get_chart_1"),
    path('get_chart_2/', views.get_chart_2, name="get_chart_2"),
    path('get_chart_3/', views.get_chart_3, name="get_chart_3"),
    path('get_chart_4/', views.get_chart_4, name="get_chart_4"),
    path('get_chart_5/', views.get_chart_5, name="get_chart_5"),
]
