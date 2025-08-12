# aqui é onde definimos os endpoints da nossa aplicação
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.login, name='login'),
    path('registerComprador/', views.registerComprador, name='registerComprador'),
]
