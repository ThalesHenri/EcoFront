from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Comprador, Vendedor, Pacote, Pedido, Pagamento, Avaliacao

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo', 'is_staff', 'date_joined')
    list_filter = ('tipo', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo', 'email')}),
    )

@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'user', 'telefone', 'data_cadastro')
    list_filter = ('data_cadastro',)
    search_fields = ('nome', 'user__email', 'telefone')

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_empresa', 'representante', 'cnpj', 'data_cadastro')
    list_filter = ('data_cadastro',)
    search_fields = ('nome_empresa', 'representante', 'cnpj', 'user__email')

@admin.register(Pacote)
class PacoteAdmin(admin.ModelAdmin):
    list_display = ('nome_pacote', 'vendedor', 'categoria', 'preco', 'quant_disponivel')
    list_filter = ('categoria', 'vendedor')
    search_fields = ('nome_pacote', 'vendedor__nome_empresa')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'comprador', 'pacote', 'preco_total', 'status_pedido', 'status_pagamento', 'data_pedido')
    list_filter = ('status_pedido', 'status_pagamento', 'data_pedido')
    search_fields = ('comprador__nome', 'pacote__nome_pacote')

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'solicitante', 'metodo', 'status_pagamento', 'data_compra')
    list_filter = ('metodo', 'status_pagamento', 'data_compra')

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('comprador', 'vendedor', 'avaliacao', 'data_avaliacao')
    list_filter = ('avaliacao', 'data_avaliacao')
    search_fields = ('comprador__nome', 'vendedor__nome_empresa')