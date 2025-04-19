from django.contrib import admin
from .models import (
    BaseConsolidada,
    ArquivoProcessado,
    RegistroRevisao
)

@admin.register(BaseConsolidada)
class BaseConsolidadaAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'cliente', 'cidade', 'data_tecnica', 'aging_resumo')
    search_fields = ('pedido', 'cliente', 'cidade')
    list_filter = ('aging_resumo', 'carteira', 'esteira')

@admin.register(ArquivoProcessado)
class ArquivoProcessadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_arquivo', 'status', 'usuario', 'data_processamento')
    list_filter = ('tipo_arquivo', 'status', 'data_processamento')
    search_fields = ('nome', 'usuario__username')

@admin.register(RegistroRevisao)
class RegistroRevisaoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'status_anterior', 'status_atual', 'usuario', 'data_revisao')
    search_fields = ('pedido', 'status_anterior', 'status_atual')
    list_filter = ('data_revisao', 'usuario')
