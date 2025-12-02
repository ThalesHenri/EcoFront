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
    path('excluir-pedido/<int:pedido_id>/', views.excluir_pedido, name='excluir_pedido'),
    path('cancelar-pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('fazer-pedido/<int:pacote_id>/', views.fazer_pedido, name='fazer_pedido'),
    path('estabelecimento/<int:vendedor_id>/', views.estabelescimento, name='estabelecimento'),
    path('pagamento-sucesso/', views.pagamentoSucesso, name='pagamento_sucesso'),
    path('pagamento-falha/', views.pagamentoFalha, name='pagamento_falha'),
    path('pagamento-pendente/', views.pagamentoPendente, name='pagamento_pendente'),
    
    # Vendedor
    path('cadastrar-pacote/', views.cadastrar_pacote, name='cadastrar_pacote'),
    path('meus-pacotes/', views.meus_pacotes, name='meus_pacotes'),
    path('editar-pacote/<int:pacote_id>/', views.editar_pacote, name='editar_pacote'),
    path('excluir-pacote/<int:pacote_id>/', views.excluir_pacote, name='excluir_pacote'),
    path('pedidos-recebidos/', views.pedidos_recebidos, name='pedidos_recebidos'),
    path('detalhes-pedido-vendedor/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),
    
    # URLs antigas para compatibilidade
    path('registerComprador/', views.registerComprador, name='registerComprador'),
]