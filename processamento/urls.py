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
    path('revisao/registro/<str:pedido>/atualizar-pendencia/', views.atualizar_pendencia_macro, name='atualizar_pendencia_macro'),
    path('revisao/exportar/', views.exportar_revisao_excel, name='exportar_revisao_excel'),
    path('api/arquivo-detalhes/<int:arquivo_id>/', views.arquivo_detalhes, name='arquivo_detalhes'),
    
    # Rotas para gerenciamento de usuários
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/adicionar/', views.criar_usuario, name='criar_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),
    
    # Rota de logout personalizada que aceita GET
    path('logout/', views.custom_logout, name='custom_logout'),
] 