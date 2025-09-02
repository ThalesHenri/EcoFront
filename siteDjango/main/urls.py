from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/comprador/', views.register_comprador, name='register_comprador'),
    path('register/vendedor/', views.register_vendedor, name='register_vendedor'),
    
    # Dashboards
    path('dashboard/comprador/', views.dashboard_comprador, name='dashboard_comprador'),
    path('dashboard/vendedor/', views.dashboard_vendedor, name='dashboard_vendedor'),
    
    # Comprador
    path('pacotes/', views.pacotes_list, name='pacotes_list'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('fazer-pedido/<int:pacote_id>/', views.fazer_pedido, name='fazer_pedido'),
    path('estabelecimento/<int:vendedor_id>/', views.estabelescimento, name='estabelecimento'),
    
    # Vendedor
    path('cadastrar-pacote/', views.cadastrar_pacote, name='cadastrar_pacote'),
    path('meus-pacotes/', views.meus_pacotes, name='meus_pacotes'),
    path('pedidos-recebidos/', views.pedidos_recebidos, name='pedidos_recebidos'),
    path('atualizar-pedido/<int:pedido_id>/', views.atualizar_pedido, name='atualizar_pedido'),
    
    # URLs antigas para compatibilidade
    path('registerComprador/', views.registerComprador, name='registerComprador'),
]