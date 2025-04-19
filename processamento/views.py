from django.shortcuts import render, get_object_or_404, redirect
import os
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from .models import ArquivoProcessado, RegistroRevisao, BaseConsolidada
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.generic import TemplateView, ListView
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import tempfile
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from django.db import transaction
import numpy as np
import warnings
from django.contrib import messages
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models.functions import TruncDate
from .modules.custom_filters import get_filtro
from .modules.database_updates import atualizar_pedidos_report_b2b, atualizar_rede_externa
from .modules.business_rules import processar_regras_negocio
import openpyxl

# Create your views here.

@login_required
def home(request):
    return render(request, 'processamento/home.html')

@login_required
def upload_arquivos(request):
    if request.method == 'POST':
        if 'arquivo' not in request.FILES and 'processar_regras' not in request.POST:
            return JsonResponse({
                'success': False,
                'message': 'Nenhum arquivo foi enviado.'
            }, status=400)
            
        try:
            if 'processar_regras' in request.POST:
                print("Iniciando processamento das regras de negócio...")
                # Obter todos os registros do banco
                registros = BaseConsolidada.objects.all()
                
                # Converter para DataFrame
                df = pd.DataFrame(list(registros.values()))
                
                # Processar regras de negócio
                resultado = processar_regras_negocio(df)
                
                if resultado['success']:
                    df_atualizado = resultado['df_atualizado']
                    total_atualizados = resultado['resultados']['total_atualizados']
                    
                    # Atualizar o banco de dados
                    print("Atualizando banco de dados...")
                    atualizados = 0
                    erros = 0
                    
                    # Processar cada registro individualmente
                    for pedido, row in df_atualizado.iterrows():
                        try:
                            # Usar transação atômica para cada registro
                            with transaction.atomic():
                                registro = BaseConsolidada.objects.get(pedido=pedido)
                                registro.tipo_entrega = row['tipo_entrega']
                                registro.data_sae = row['data_sae']
                                registro.esteira = row['esteira']
                                registro.segmento_v3 = row['segmento_v3']
                                registro.sla_tecnica = row['sla_tecnica']
                                registro.status_rede = row['status_rede']
                                registro.agrupado = row['agrupado']
                                registro.pendencia_macro = row['pendencia_macro']
                                registro.estimativa = row['estimativa']
                                registro.save()
                                atualizados += 1
                                
                                if atualizados % 1000 == 0:
                                    print(f"Atualizados {atualizados} registros...")
                                    
                        except BaseConsolidada.DoesNotExist:
                            print(f"Registro não encontrado para o pedido: {pedido}")
                            erros += 1
                            continue
                        except Exception as e:
                            print(f"Erro ao atualizar registro {pedido}: {str(e)}")
                            erros += 1
                            continue
                    
                    print(f"Processamento concluído. Total de registros atualizados: {atualizados}, Erros: {erros}")
                    messages.success(request, f"Regras de negócio processadas com sucesso. Total de registros atualizados: {atualizados}, Erros: {erros}")
                else:
                    print(f"Erro durante o processamento: {resultado['error']}")
                    messages.error(request, f"Erro durante o processamento das regras de negócio: {resultado['error']}")
                
                return redirect('upload_arquivos')
            
            # Processamento normal de arquivo
            arquivo = request.FILES['arquivo']
            
            # Salvar o arquivo temporariamente
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(arquivo.read())
            temp_file.close()
            
            # Verificar o tipo de arquivo
            xls = pd.ExcelFile(temp_file.name)
            print(f"Abas disponíveis no arquivo: {xls.sheet_names}")
            
            # Verificar se é base de Rede Externa
            if 'ANALITICO' in xls.sheet_names:
                df = pd.read_excel(temp_file.name, sheet_name='ANALITICO')
                print(f"Colunas encontradas na aba ANALITICO: {df.columns.tolist()}")
                
                colunas_rede = ['PEDIDO', 'CONTRATADA', 'Prazo Rede']
                colunas_arquivo = [col.upper().strip() for col in df.columns]
                colunas_rede_norm = [col.upper().strip() for col in colunas_rede]
                
                if all(col in colunas_arquivo for col in colunas_rede_norm):
                    try:
                        stats = atualizar_rede_externa(temp_file.name)
                        messages.success(request, f'''
                            Arquivo de Rede Externa processado com sucesso!
                            Total na base de Rede: {stats['total_rede']}
                            Total na base do sistema: {stats['total_base']}
                            Pedidos atualizados: {stats['atualizados']}
                        ''')
                    except Exception as e:
                        raise Exception(f'Erro ao processar base de Rede Externa: {str(e)}')
                else:
                    raise Exception(f'''
                        Colunas necessárias não encontradas na aba ANALITICO.
                        Colunas encontradas: {df.columns.tolist()}
                        Colunas esperadas: {colunas_rede}
                    ''')
            # Verificar se é report B2B
            elif 'Report' in xls.sheet_names:
                df = pd.read_excel(temp_file.name, sheet_name='Report')
                print(f"Colunas encontradas na aba Report: {df.columns.tolist()}")
                
                colunas_b2b = ['Pedido', 'Cliente', 'Cidade', 'Esteira']
                colunas_arquivo = [col.upper().strip() for col in df.columns]
                colunas_b2b_norm = [col.upper().strip() for col in colunas_b2b]
                
                if all(col in colunas_arquivo for col in colunas_b2b_norm):
                    try:
                        stats = atualizar_pedidos_report_b2b(temp_file.name)
                        messages.success(request, f'''
                            Arquivo B2B processado com sucesso!
                            Total no report: {stats['total_report']}
                            Total na base: {stats['total_base']}
                            Pedidos criados: {stats['criados']}
                            Pedidos atualizados: {stats['atualizados']}
                            Pedidos removidos: {stats['removidos']}
                        ''')
                    except Exception as e:
                        raise Exception(f'Erro ao processar report B2B: {str(e)}')
                else:
                    raise Exception(f'''
                        Colunas necessárias não encontradas na aba Report.
                        Colunas encontradas: {df.columns.tolist()}
                        Colunas esperadas: {colunas_b2b}
                    ''')
            else:
                raise Exception(f'''
                    Nenhuma aba válida encontrada no arquivo.
                    Abas disponíveis: {xls.sheet_names}
                    Abas esperadas: ANALITICO (para Rede Externa) ou Report (para B2B)
                ''')
            
            # Remover arquivo temporário
            os.unlink(temp_file.name)
            return JsonResponse({'success': True})
            
        except Exception as e:
            # Remover arquivo temporário em caso de erro
            if 'temp_file' in locals():
                os.unlink(temp_file.name)
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return render(request, 'processamento/upload.html')

@login_required
def lista_arquivos(request):
    arquivos = ArquivoProcessado.objects.all().order_by('-data_processamento')
    return render(request, 'processamento/lista_arquivos.html', {'arquivos': arquivos})

@login_required
def revisao(request):
    return render(request, 'processamento/revisao.html')

@login_required
def revisao_data(request):
    # Obter parâmetros do DataTable
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search = request.GET.get('search[value]', '')
    segmento = request.GET.get('segmento', '')
    tipo = request.GET.get('tipo', 'revisar')
    
    # Obter parâmetros de ordenação
    order_column = request.GET.get('order[0][column]', '0')
    order_dir = request.GET.get('order[0][dir]', 'desc')
    
    # Mapear colunas para campos do modelo
    column_map = {
        '0': 'pedido',
        '1': 'dias_carteira_atual',
        '2': 'data_tecnica',
        '3': 'carteira',
        '4': 'pendencia_macro',
        '5': 'estimativa',
        '6': 'segmento_v3'
    }
    
    # Obter filtros do módulo
    filtros = get_filtro(tipo)
    
    # Construir a query base
    query = Q()
    
    # Aplicar filtros baseado no tipo selecionado
    if 'pendencia_macro' in filtros:
        query &= Q(pendencia_macro__in=filtros['pendencia_macro'])
    if 'classificacao_resumo_atual' in filtros:
        query &= Q(classificacao_resumo_atual=filtros['classificacao_resumo_atual'])
    if 'esteira' in filtros:
        query &= Q(esteira=filtros['esteira'])
    
    # Aplicar filtro por segmento se fornecido
    if segmento:
        query &= Q(segmento_v3=segmento)
    
    # Aplicar filtro de busca global
    if search:
        query &= (
            Q(pedido__icontains=search) |
            Q(cliente__icontains=search) |
            Q(carteira__icontains=search) |
            Q(pendencia_macro__icontains=search) |
            Q(estimativa__icontains=search) |
            Q(segmento_v3__icontains=search)
        )
    
    # Obter total de registros
    total = BaseConsolidada.objects.filter(query).count()
    
    # Obter registros filtrados com ordenação
    order_field = column_map.get(order_column, 'pedido')
    if order_dir == 'desc':
        order_field = f'-{order_field}'
    
    registros = BaseConsolidada.objects.filter(query).order_by(order_field)
    filtered = registros.count()
    
    # Aplicar paginação
    registros = registros[start:start + length]
    
    # Preparar dados para resposta
    data = []
    for registro in registros:
        data.append({
            'pedido': registro.pedido,
            'dias_carteira_atual': registro.dias_carteira_atual or '-',
            'data_tecnica': registro.data_tecnica.strftime('%d/%m/%Y') if registro.data_tecnica else '-',
            'carteira': registro.carteira or '-',
            'pendencia_macro': registro.pendencia_macro or '-',
            'estimativa': registro.estimativa or '-',
            'segmento_v3': registro.segmento_v3 or '-'
        })
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered,
        'data': data
    })

@login_required
def revisao_segmentos(request):
    tipo = request.GET.get('tipo', 'revisar')
    print(f"Tipo recebido: {tipo}")
    
    # Obter filtros do módulo
    filtros = get_filtro(tipo)
    print(f"Filtros obtidos: {filtros}")
    
    # Construir a query base
    query = Q()
    
    # Aplicar filtros baseado no tipo selecionado
    if 'pendencia_macro' in filtros:
        query &= Q(pendencia_macro__in=filtros['pendencia_macro'])
        print(f"Query após pendencia_macro: {query}")
    if 'classificacao_resumo_atual' in filtros:
        query &= Q(classificacao_resumo_atual=filtros['classificacao_resumo_atual'])
        print(f"Query após classificacao_resumo_atual: {query}")
    if 'esteira' in filtros:
        query &= Q(esteira=filtros['esteira'])
        print(f"Query após esteira: {query}")
    
    # Debug: Verificar valores únicos no banco
    pendencias_unicas = BaseConsolidada.objects.values_list('pendencia_macro', flat=True).distinct()
    classificacoes_unicas = BaseConsolidada.objects.values_list('classificacao_resumo_atual', flat=True).distinct()
    esteiras_unicas = BaseConsolidada.objects.values_list('esteira', flat=True).distinct()
    
    print(f"Pendências únicas no banco: {list(pendencias_unicas)}")
    print(f"Classificações únicas no banco: {list(classificacoes_unicas)}")
    print(f"Esteiras únicas no banco: {list(esteiras_unicas)}")
    
    # Obter total geral
    total_geral = BaseConsolidada.objects.filter(query).count()
    print(f"Total geral após filtros: {total_geral}")
    
    # Obter contagem por segmento
    segmentos = BaseConsolidada.objects.filter(query).values('segmento_v3').annotate(
        total=Count('id')
    ).order_by('segmento_v3')
    
    # Preparar resposta
    data = {
        'total_geral': total_geral,
        'segmentos': [
            {
                'segmento': item['segmento_v3'] or 'Não Informado',
                'total': item['total']
            }
            for item in segmentos
        ]
    }
    
    print(f"Resposta final: {data}")
    return JsonResponse(data)

@method_decorator(login_required, name='dispatch')
class BaseConsolidadaView(ListView):
    model = BaseConsolidada
    template_name = 'processamento/base_consolidada.html'
    context_object_name = 'registros'
    paginate_by = 50

    def get_queryset(self):
        return BaseConsolidada.objects.all().order_by('-created_at')

@login_required
def base_consolidada_data(request):
    # Obter parâmetros do DataTables
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 25))
    
    # Obter parâmetros de ordenação
    order_column = request.GET.get('order[0][column]', '0')
    order_dir = request.GET.get('order[0][dir]', 'desc')
    
    # Mapear colunas para campos do modelo
    column_map = {
        '0': 'pedido',
        '1': 'dias_carteira_atual',
        '2': 'data_tecnica',
        '3': 'carteira',
        '4': 'pendencia_macro',
        '5': 'estimativa',
        '6': 'segmento_v3'
    }
    
    # Obter parâmetros de filtro
    pedido = request.GET.get('pedido', '')
    cliente = request.GET.get('cliente', '')
    spe = request.GET.get('spe', '')
    atp = request.GET.get('atp', '')
    
    # Construir query
    query = Q()
    if pedido:
        query &= Q(pedido__icontains=pedido)
    if cliente:
        query &= Q(cliente__icontains=cliente)
    if spe:
        query &= Q(spe__icontains=spe)
    if atp:
        query &= Q(atp__icontains=atp)
    
    # Obter total de registros
    total = BaseConsolidada.objects.count()
    
    # Obter registros filtrados com ordenação
    order_field = column_map.get(order_column, 'pedido')
    if order_dir == 'desc':
        order_field = f'-{order_field}'
    
    registros = BaseConsolidada.objects.filter(query).order_by(order_field)
    filtered = registros.count()
    
    # Aplicar paginação
    registros = registros[start:start + length]
    
    # Preparar dados
    data = []
    for registro in registros:
        data.append({
            'pedido': registro.pedido,
            'dias_carteira_atual': registro.dias_carteira_atual or '-',
            'data_tecnica': registro.data_tecnica.strftime('%d/%m/%Y') if registro.data_tecnica else '-',
            'carteira': registro.carteira or '-',
            'pendencia_macro': registro.pendencia_macro or '-',
            'estimativa': registro.estimativa or '-',
            'segmento_v3': registro.segmento_v3 or '-'
        })
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered,
        'data': data
    })

@login_required
def detalhe_registro(request, pedido):
    registro = get_object_or_404(BaseConsolidada, pedido=pedido)
    revisao = RegistroRevisao.objects.filter(pedido=pedido).first()
    
    context = {
        'registro': registro,
        'revisao': revisao,
    }
    
    return render(request, 'processamento/detalhe_registro.html', context)

@login_required
def revisar_registro(request, pedido):
    registro = get_object_or_404(BaseConsolidada, pedido=pedido)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        observacao = request.POST.get('observacao')
        
        revisao = RegistroRevisao.objects.create(
            pedido=pedido,
            status=status,
            observacao=observacao,
            usuario=request.user
        )
        
        return JsonResponse({'success': True, 'revisao_id': revisao.id})
    
    context = {
        'registro': registro,
    }
    
    return render(request, 'processamento/revisar_registro.html', context)

@login_required
def confirmar_revisao(request, pedido):
    revisao = get_object_or_404(RegistroRevisao, pedido=pedido)
    revisao.confirmado = True
    revisao.save()
    
    return JsonResponse({'success': True})

@login_required
def rejeitar_revisao(request, pedido):
    revisao = get_object_or_404(RegistroRevisao, pedido=pedido)
    revisao.confirmado = False
    revisao.save()
    
    return JsonResponse({'success': True})

@login_required
def get_registro_detalhes(request, pedido):
    try:
        registro = BaseConsolidada.objects.get(pedido=pedido)
        data = {
            'pedido': registro.pedido,
            'cliente': registro.cliente,
            'cidade': registro.cidade,
            'esteira': registro.esteira,
            'esteira_regionalizada': registro.esteira_regionalizada,
            'seg_resumo': registro.seg_resumo,
            'produto': registro.produto,
            'servico': registro.servico,
            'classificacao': registro.classificacao_resumo_atual,
            'cadeia_pendencias_descricao': registro.cadeia_pendencias_descricao,
            'carteira': registro.carteira,
            'dias_carteira_atual': registro.dias_carteira_atual,
            'data_tecnica': registro.data_tecnica,
            'osx': registro.osx,
            'motivo_pta_cod': registro.motivo_pta_cod,
            'num_wcd': registro.wcd,
            'tm_tec_total': registro.tm_tec_total,
            'delta_rec_liq': registro.delta_rec_liq,
            'aging_resumo': registro.aging_resumo,
            'origem_pend': registro.origem_pend,
            'segmento_v3': registro.segmento_v3,
            'sla_tecnica': registro.sla_tecnica,
            'quebra_esteira': registro.quebra_esteira,
            'projetos': registro.projetos,
            'projetos_lote': registro.projetos_lote,
            'tecnologia_report': registro.tecnologia_report,
            'draft_encontrado': registro.draft_encontrado,
            'data_criacao_draft': registro.data_criacao_draft,
            'tarefa_atual_draft': registro.tarefa_atual_draft,
            'status_rede': registro.status_rede,
            'eps_rede': registro.eps_rede,
            'data_rede': registro.data_rede,
            'tipo_entrega': registro.tipo_entrega,
            'data_sae': registro.data_sae,
            'agrupado': registro.agrupado,
            'pendencia_macro': registro.pendencia_macro,
            'estimativa': registro.estimativa
        }
        return JsonResponse({'success': True, 'registro': data})
    except BaseConsolidada.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Registro não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def get_registro_detalhes_base(request, pedido):
    try:
        registro = BaseConsolidada.objects.get(pedido=pedido)
        data = {
            'cliente': registro.cliente,
            'cidade': registro.cidade,
            'esteira': registro.esteira,
            'esteira_regionalizada': registro.esteira_regionalizada,
            'seg_resumo': registro.seg_resumo,
            'produto': registro.produto,
            'servico': registro.servico,
            'classificacao_resumo_atual': registro.classificacao_resumo_atual,
            'cadeia_pendencias_descricao': registro.cadeia_pendencias_descricao,
            'carteira': registro.carteira,
            'dias_carteira_atual': registro.dias_carteira_atual,
            'data_tecnica': registro.data_tecnica.strftime('%d/%m/%Y') if registro.data_tecnica else None,
            'osx': registro.osx,
            'motivo_pta_cod': registro.motivo_pta_cod,
            'status_rede': registro.status_rede,
            'eps_rede': registro.eps_rede,
            'data_rede': registro.data_rede.strftime('%d/%m/%Y') if registro.data_rede else None,
            'tipo_entrega': registro.tipo_entrega,
            'data_sae': registro.data_sae.strftime('%d/%m/%Y') if registro.data_sae else None,
            'agrupado': registro.agrupado,
            'pendencia_macro': registro.pendencia_macro,
            'estimativa': registro.estimativa,
            'wcd': registro.wcd,
            'num_atp': registro.num_atp,
            'draft_encontrado': registro.draft_encontrado,
            'data_criacao_draft': registro.data_criacao_draft.strftime('%d/%m/%Y') if registro.data_criacao_draft else None
        }
        return JsonResponse(data)
    except BaseConsolidada.DoesNotExist:
        return JsonResponse({'error': 'Registro não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def detalhe_revisao(request, pedido):
    registro = get_object_or_404(BaseConsolidada, pedido=pedido)
    return render(request, 'processamento/detalhe_registro.html', {'registro': registro})

@login_required
def exportar_base_excel(request):
    try:
        # Obtém todos os registros da base consolidada
        registros = BaseConsolidada.objects.all()
        
        # Converte para DataFrame
        df = pd.DataFrame(list(registros.values()))
        
        # Remove timezone dos campos datetime
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = df[col].dt.tz_localize(None)
        
        # Define o caminho do arquivo modelo
        arquivo_modelo = os.path.join(settings.MEDIA_ROOT, 'modelos', 'modelo_batimento.xlsx')
        
        # Carrega o arquivo modelo
        livro = openpyxl.load_workbook(arquivo_modelo)
        
        # Obtém a aba Base_Consolidada
        sheet = livro['Base_Consolidada']
        
        # Limpa o conteúdo existente
        sheet.delete_rows(1, sheet.max_row)
        
        # Atualiza os títulos das colunas
        for j, col_name in enumerate(df.columns, start=1):
            sheet.cell(row=1, column=j, value=col_name)
        
        # Atualiza o DataFrame na planilha
        for i, row in enumerate(df.values, start=2):
            for j, value in enumerate(row, start=1):
                sheet.cell(row=i, column=j, value=value)
        
        # Gera o nome do arquivo com timestamp
        now = datetime.now()
        formatted_date = now.strftime("%d_%m_%H_%M")
        arquivo_saida = f"base_batimento_report_{formatted_date}.xlsx"
        
        # Salva o arquivo com o novo nome
        livro.save(arquivo_saida)
        
        # Lê o arquivo para download
        with open(arquivo_saida, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={arquivo_saida}'
        
        # Remove o arquivo temporário
        os.remove(arquivo_saida)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao exportar base: {str(e)}')
        return redirect('upload_arquivos')
