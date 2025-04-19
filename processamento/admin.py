from django.contrib import admin
from .models import (
    BaseConsolidada,
    ArquivoProcessado,
    RegistroRevisao,
    PerfilUsuario
)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'perfil', 'created_at', 'updated_at')
    list_filter = ('perfil',)
    search_fields = ('usuario__username', 'usuario__email')
    date_hierarchy = 'created_at'

@admin.register(BaseConsolidada)
class BaseConsolidadaAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'cliente', 'cidade', 'esteira', 'carteira', 'data_tecnica')
    list_filter = ('carteira', 'esteira')
    search_fields = ('pedido', 'cliente', 'cidade')
    date_hierarchy = 'created_at'

@admin.register(ArquivoProcessado)
class ArquivoProcessadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_arquivo', 'status', 'data_processamento', 'usuario', 'registros_afetados')
    list_filter = ('tipo_arquivo', 'status')
    search_fields = ('nome', 'usuario__username')
    date_hierarchy = 'data_processamento'

@admin.register(RegistroRevisao)
class RegistroRevisaoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'status_anterior', 'status_atual', 'data_revisao', 'usuario')
    list_filter = ('status_atual',)
    search_fields = ('pedido', 'usuario__username')
    date_hierarchy = 'data_revisao'
