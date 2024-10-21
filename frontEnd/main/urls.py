from django.urls import path
from . import views



urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('mostrarProdutos/',views.mostrarProdutos,name='mostrarProdutos'),
    path('cadastrarProduto/',views.cadastrarProduto,name='cadastrarProduto'),
    path('cadastrarProduto/sendForm/',views.cadastrarProdutoForm, name='cadastrarProdutoForm'),
    path('cadastrarUsuario/',views.cadastrarUsuario,name='cadastrarUsuario'),
    path('cadastrarUsuario/sendForm/',views.cadastrarUsuarioForm,name='cadastrarUsuarioForm'),
    path('quemSomos/',views.quemSomos,name='quemSomos'),
    path('login/',views.login,name='login'),
    path('login/event/',views.loginEvent,name='loginEvent'),
    path('logout/',views.logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    
    
]
