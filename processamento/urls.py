from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_arquivos, name='upload_arquivos'),
    path('upload/exportar/', views.exportar_base_excel, name='exportar_base_excel'),
    path('lista_arquivos/', views.lista_arquivos, name='lista_arquivos'),
    path('revisao/', views.revisao, name='revisao'),
    path('revisao/data/', views.revisao_data, name='revisao_data'),
    path('revisao/segmentos/', views.revisao_segmentos, name='revisao_segmentos'),
    path('revisao/registro/<str:pedido>/', views.detalhe_revisao, name='detalhe_revisao'),
    path('revisao/registro/<str:pedido>/detalhes/', views.get_registro_detalhes, name='get_registro_detalhes'),
    path('base-consolidada/', views.BaseConsolidadaView.as_view(), name='base_consolidada'),
    path('base-consolidada/data/', views.base_consolidada_data, name='base_consolidada_data'),
    path('base-consolidada/registro/<str:pedido>/', views.detalhe_registro, name='detalhe_registro'),
    path('base-consolidada/registro/<str:pedido>/revisar/', views.revisar_registro, name='revisar_registro'),
    path('base-consolidada/registro/<str:pedido>/confirmar/', views.confirmar_revisao, name='confirmar_revisao'),
    path('base-consolidada/registro/<str:pedido>/rejeitar/', views.rejeitar_revisao, name='rejeitar_revisao'),
    path('base-consolidada/registro/<str:pedido>/detalhes/', views.get_registro_detalhes_base, name='get_registro_detalhes_base'),
] 