from django.contrib import admin

# Register your models here.
from .models import Usuario, Produto

# Customizing the admin display for Usuario
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'responsavel', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('nome', 'cnpj', 'responsavel')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

# Customizing the admin display for Produto
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'peso', 'quantidade', 'frete', 'preco', 'dataValid')
    search_fields = ('nome', 'marca')
    list_filter = ('frete', 'dataValid')

# Registering the models in the admin site
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Produto, ProdutoAdmin)