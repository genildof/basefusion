from django.db import transaction
from processamento.models import BaseConsolidada
import pandas as pd
import numpy as np
import warnings

# Desative os avisos
warnings.simplefilter("ignore")

# Nome da sheet do report B2B
REPORT_B2B_SHEET = 'Export'
# Nome da sheet da base de Rede Externa
REDE_EXTERNA_SHEET = 'ANALITICO'

def atualizar_pedidos_report_b2b(caminho_arquivo):
    """
    Atualiza os pedidos na base de dados a partir do report B2B.
    
    Args:
        caminho_arquivo (str): Caminho do arquivo Excel do report B2B
        
    Returns:
        dict: Dicionário com estatísticas da atualização
    """
    try:
        # Ler o arquivo Excel
        df = pd.read_excel(caminho_arquivo)
        df = df.replace({np.nan: None})
        
        # Obter total no report
        total_report = len(df)
        
        # Obter total na base
        total_base = BaseConsolidada.objects.count()
        
        # Contadores
        criados = 0
        atualizados = 0
        removidos = 0
        
        # Lista de pedidos no report
        pedidos_report = set(df['Pedido'].unique())
        
        # Lista de pedidos na base
        pedidos_base = set(BaseConsolidada.objects.values_list('pedido', flat=True))
        
        # Pedidos para remover (estão na base mas não no report)
        pedidos_remover = pedidos_base - pedidos_report
        
        # Remover pedidos que não estão mais no report
        if pedidos_remover:
            BaseConsolidada.objects.filter(pedido__in=pedidos_remover).delete()
            removidos = len(pedidos_remover)
        
        # Atualizar ou criar registros
        for _, row in df.iterrows():
            try:
                # Converter datas
                data_tecnica = pd.to_datetime(row.get('DataTecnica')).date() if pd.notnull(row.get('DataTecnica')) else None
                data_criacao_draft = pd.to_datetime(row.get('DataCriaçãoDraft')).date() if pd.notnull(row.get('DataCriaçãoDraft')) else None
                data_rede = pd.to_datetime(row.get('Data_Rede')).date() if pd.notnull(row.get('Data_Rede')) else None
                data_sae = pd.to_datetime(row.get('Data_SAE')).date() if pd.notnull(row.get('Data_SAE')) else None
                
                # Criar ou atualizar registro
                registro, created = BaseConsolidada.objects.update_or_create(
                    pedido=row['Pedido'],
                    defaults={
                        'cliente': row.get('Cliente'),
                        'cidade': row.get('Cidade'),
                        'esteira': row.get('Esteira'),
                        'esteira_regionalizada': row.get('Esteira_Regionalizada'),
                        'seg_resumo': row.get('SegResumo'),
                        'produto': row.get('Produto'),
                        'servico': row.get('Servico'),
                        'classificacao_resumo_atual': row.get('Classificacao_Resumo_Atual'),
                        'cadeia_pendencias_descricao': row.get('Cadeia_Pendencias_Descricao'),
                        'carteira': row.get('Carteira'),
                        'dias_carteira_atual': row.get('Dias_CarteiraAtual'),
                        'data_tecnica': data_tecnica,
                        'osx': row.get('OSX'),
                        'motivo_pta_cod': row.get('Motivo_PTA_Cod'),
                        'wcd': row.get('Num_WCD'),
                        'num_atp': row.get('Num_ATP'),
                        'draft_encontrado': row.get('DraftEncontrado'),
                        'data_criacao_draft': data_criacao_draft,
                        'tarefa_atual_draft': row.get('TarefaAtualDraft'),
                        'tecnologia_report': row.get('Tecnologia_Report'),
                        'quebra_esteira': row.get('Quebra_Esteira'),
                        'projetos': row.get('Projetos'),
                        'projetos_lote': row.get('Projetos_Lote'),
                        'tm_tec_total': row.get('TM_Tec_Total'),
                        'delta_rec_liq': row.get('Delta_REC_LIQ'),
                        'aging_resumo': row.get('Aging Resumo'),
                        'origem_pend': row.get('Origem Pend.'),
                        'segmento_v3': row.get('Segmento_V3'),
                        'sla_tecnica': row.get('SLA_TECNICA'),
                        'status_rede': row.get('Status_Rede'),
                        'eps_rede': row.get('EPS_Rede'),
                        'data_rede': data_rede,
                        'tipo_entrega': row.get('Tipo_Entrega'),
                        'data_sae': data_sae,
                        'agrupado': row.get('Agrupado'),
                        'pendencia_macro': row.get('Pendencia_Macro'),
                        'estimativa': row.get('Estimativa')
                    }
                )
                
                if created:
                    criados += 1
                else:
                    atualizados += 1
                    
            except Exception as e:
                warnings.warn(f"Erro ao processar pedido {row.get('Pedido')}: {str(e)}")
                continue
        
        return {
            'total_report': total_report,
            'total_base': total_base,
            'criados': criados,
            'atualizados': atualizados,
            'removidos': removidos
        }
        
    except Exception as e:
        raise Exception(f"Erro ao atualizar pedidos: {str(e)}")

def atualizar_rede_externa(file_path):
    """
    Atualiza os pedidos na base de dados a partir da base de Rede Externa.
    
    Args:
        file_path (str): Caminho do arquivo Excel da base de Rede Externa
        
    Returns:
        dict: Dicionário com estatísticas da atualização
    """
    try:
        # Lê o arquivo Excel
        df = pd.read_excel(file_path, sheet_name=REDE_EXTERNA_SHEET)
        df = df.replace({np.nan: None})
        
        # Verifica se as colunas necessárias existem
        colunas_necessarias = ['PEDIDO', 'ANALISE 02', 'CONTRATADA', 'Prazo Rede']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        if colunas_faltantes:
            raise Exception(f"Colunas necessárias não encontradas no arquivo: {', '.join(colunas_faltantes)}")
        
        # Lista de pedidos da base de Rede Externa
        pedidos_rede = set(df['PEDIDO'].unique())
        
        # Lista de pedidos existentes na base do sistema
        pedidos_base = set(BaseConsolidada.objects.values_list('pedido', flat=True))
        
        # Pedidos para atualizar (existem em ambas as bases)
        pedidos_atualizar = pedidos_rede & pedidos_base
        
        # Cria um dicionário com os dados da base de Rede Externa
        dados_rede = {}
        for _, row in df.iterrows():
            try:
                pedido = str(row['PEDIDO']).strip()  # Garante que o pedido é string e remove espaços
                if not pedido:  # Pula linhas com pedido vazio
                    continue
                    
                # Converte a data, tratando possíveis erros
                data_rede = None
                if pd.notnull(row['Prazo Rede']):
                    try:
                        data_rede = pd.to_datetime(row['Prazo Rede']).date()
                    except Exception as e:
                        warnings.warn(f"Erro ao converter data do pedido {pedido}: {str(e)}")
                
                dados_rede[pedido] = {
                    'status_rede': str(row['ANALISE 02']).strip() if pd.notnull(row['ANALISE 02']) else None,
                    'eps_rede': str(row['CONTRATADA']).strip() if pd.notnull(row['CONTRATADA']) else None,
                    'data_rede': data_rede
                }
            except Exception as e:
                warnings.warn(f"Erro ao processar linha do pedido {row.get('PEDIDO', 'DESCONHECIDO')}: {str(e)}")
                continue
        
        # Atualiza pedidos existentes
        atualizados = 0
        with transaction.atomic():
            for pedido in pedidos_atualizar:
                try:
                    if pedido in dados_rede:  # Verifica se temos dados para este pedido
                        BaseConsolidada.objects.filter(pedido=pedido).update(
                            status_rede=dados_rede[pedido]['status_rede'],
                            eps_rede=dados_rede[pedido]['eps_rede'],
                            data_rede=dados_rede[pedido]['data_rede']
                        )
                        atualizados += 1
                except Exception as e:
                    warnings.warn(f"Erro ao atualizar pedido {pedido}: {str(e)}")
                    continue
        
        return {
            'total_rede': len(pedidos_rede),
            'total_base': len(pedidos_base),
            'atualizados': atualizados
        }
        
    except Exception as e:
        raise Exception(f"Erro ao atualizar rede externa: {str(e)}") 