from django.db import transaction
from processamento.models import BaseConsolidada
import pandas as pd
import numpy as np
import warnings
from django.db.models import Q

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
        # Lista das colunas específicas a serem importadas
        colunas_necessarias = [
            'Pedido', 'Dias_CarteiraAtual', 'TM_Tec_Total', 'Num_WCD', 'Num_ATP',
            'Classificacao_Resumo_Atual', 'SegResumo', 'Quebra_Esteira', 'Esteira', 
            'Esteira_Regionalizada', 'Segmento_V3', 'Carteira', 'Cliente', 'Cidade', 
            'OSX', 'Cadeia_Pendencias_Descricao', 'DataTecnica', 'Produto', 'Servico', 
            'Delta_REC_LIQ', 'Tecnologia_Report', 'Aging Resumo', 'Projetos', 'Projetos_Lote',
            'Motivo_PTA_Cod', 'Origem Pend.', 'SLA_TECNICA', 'DraftEncontrado', 
            'TarefaAtualDraft', 'DataCriaçãoDraft'
        ]
        
        # Ler o arquivo Excel - primeiro verificamos todas as colunas disponíveis
        df_preview = pd.read_excel(caminho_arquivo, nrows=1)
        
        # Verificar colunas disponíveis no arquivo
        colunas_disponiveis = set(df_preview.columns)
        colunas_a_importar = [col for col in colunas_necessarias if col in colunas_disponiveis]
        
        # Registrar colunas não encontradas
        colunas_faltantes = [col for col in colunas_necessarias if col not in colunas_disponiveis]
        if colunas_faltantes:
            print(f"Aviso: As seguintes colunas não foram encontradas no arquivo: {', '.join(colunas_faltantes)}")
        
        # Verificar se coluna Pedido está disponível (obrigatória)
        if 'Pedido' not in colunas_a_importar:
            raise Exception("Coluna 'Pedido' não encontrada no arquivo. Esta coluna é obrigatória.")
        
        # Verificar se coluna Esteira está disponível (importante para filtro)
        if 'Esteira' not in colunas_a_importar:
            raise Exception("Coluna 'Esteira' não encontrada no arquivo. Esta coluna é necessária para filtragem.")
        
        # Ler novamente o arquivo Excel com apenas as colunas necessárias
        df = pd.read_excel(caminho_arquivo, usecols=colunas_a_importar)
        
        # Verificar se há uma coluna 'Esteira'
        if 'Esteira' not in df.columns:
            raise Exception("Coluna 'Esteira' não encontrada no arquivo após leitura seletiva")
        
        # Total de registros brutos no arquivo
        total_registros_brutos = len(df)
        
        # Filtragem 1: Remover linhas com Esteira vazia (NaN, None, string vazia)
        df = df[~df['Esteira'].isna() & (df['Esteira'] != '')]
        
        # Total de registros após filtrar esteiras vazias
        total_apos_filtro_esteira = len(df)
        
        # Substituir NaN por None para permitir inserção no banco
        df = df.replace({np.nan: None})
        
        # Obter total no report após filtros
        total_report = len(df)
        
        # Obter total na base antes da atualização
        total_base = BaseConsolidada.objects.count()
        
        # Contadores
        criados = 0
        atualizados = 0
        removidos = 0
        ignorados = total_registros_brutos - total_report
        
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
        
        # Remover registros existentes onde Esteira está preenchida mas outras colunas importantes estão nulas
        # Identificando colunas críticas - aquelas que nunca deveriam ser nulas quando a esteira está definida
        colunas_criticas = ['cliente', 'cidade', 'produto']
        
        # Remover registros com colunas críticas nulas
        registros_invalidos = BaseConsolidada.objects.filter(
            esteira__isnull=False
        ).filter(
            Q(cliente__isnull=True) | Q(cliente='') |
            Q(cidade__isnull=True) | Q(cidade='') |
            Q(produto__isnull=True) | Q(produto='')
        )
        
        # Contabilizar registros inválidos para remoção
        total_invalidos = registros_invalidos.count()
        if total_invalidos > 0:
            registros_invalidos.delete()
            print(f"Removidos {total_invalidos} registros inválidos com esteira definida mas colunas críticas vazias")
        
        # Atualizar ou criar registros
        for _, row in df.iterrows():
            try:
                # Verificação adicional: pular linhas onde pedido está vazio
                if pd.isna(row.get('Pedido')) or not str(row.get('Pedido')).strip():
                    continue
                
                # Verificação adicional: pular linhas onde esteira está vazia
                if pd.isna(row.get('Esteira')) or not str(row.get('Esteira')).strip():
                    continue
                
                # Verificação adicional: pular linhas onde cliente e cidade estão vazios (provavelmente linha de observação)
                if (pd.isna(row.get('Cliente')) or not str(row.get('Cliente')).strip()) and \
                   (pd.isna(row.get('Cidade')) or not str(row.get('Cidade')).strip()):
                    continue
                
                # Converter datas
                data_tecnica = pd.to_datetime(row.get('DataTecnica')).date() if pd.notnull(row.get('DataTecnica')) else None
                data_criacao_draft = pd.to_datetime(row.get('DataCriaçãoDraft')).date() if pd.notnull(row.get('DataCriaçãoDraft')) else None
                
                # Preparar defaults com apenas os campos disponíveis
                defaults = {
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
                }
                
                # Limpar defaults removendo chaves com valor None que não estavam no arquivo
                defaults = {k: v for k, v in defaults.items() if k.lower() in [col.lower() for col in colunas_a_importar] or v is not None}
                
                # Criar ou atualizar registro
                registro, created = BaseConsolidada.objects.update_or_create(
                    pedido=row['Pedido'],
                    defaults=defaults
                )
                
                if created:
                    criados += 1
                else:
                    atualizados += 1
                    
            except Exception as e:
                warnings.warn(f"Erro ao processar pedido {row.get('Pedido')}: {str(e)}")
                continue
        
        return {
            'total_registros_brutos': total_registros_brutos,
            'total_ignorados': ignorados,
            'total_report': total_report,
            'total_base': total_base,
            'criados': criados,
            'atualizados': atualizados,
            'removidos': removidos,
            'registros_invalidos_removidos': total_invalidos,
            'colunas_importadas': len(colunas_a_importar),
            'colunas_faltantes': colunas_faltantes
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
        
        # Obtém a lista de colunas disponíveis
        colunas_disponiveis = list(df.columns)
        
        # Função auxiliar para encontrar colunas independente de maiúsculas/minúsculas
        def encontrar_coluna(nome_coluna, colunas):
            for col in colunas:
                if col.lower() == nome_coluna.lower():
                    return col
            return None
        
        # Mapeia nomes de colunas para seus equivalentes no DataFrame
        mapeamento_colunas = {
            'PEDIDO': encontrar_coluna('PEDIDO', colunas_disponiveis),
            'ANALISE 02': encontrar_coluna('ANALISE 02', colunas_disponiveis),
            'CONTRATADA': encontrar_coluna('CONTRATADA', colunas_disponiveis),
            'Prazo Rede': encontrar_coluna('Prazo Rede', colunas_disponiveis),
            'ATP/OSX': encontrar_coluna('ATP/OSX', colunas_disponiveis),
            'wcd': encontrar_coluna('wcd', colunas_disponiveis) or encontrar_coluna('WCD', colunas_disponiveis)
        }
        
        # Verifica se as colunas necessárias existem (agora incluindo ATP/OSX e wcd)
        colunas_necessarias = ['PEDIDO', 'ANALISE 02', 'CONTRATADA', 'Prazo Rede', 'ATP/OSX', 'wcd']
        colunas_faltantes = [col for col in colunas_necessarias if mapeamento_colunas[col] is None]
        if colunas_faltantes:
            raise Exception(f"Colunas necessárias não encontradas no arquivo: {', '.join(colunas_faltantes)}")
        
        # Nome real das colunas no arquivo
        coluna_pedido = mapeamento_colunas['PEDIDO']
        coluna_analise = mapeamento_colunas['ANALISE 02']
        coluna_contratada = mapeamento_colunas['CONTRATADA']
        coluna_prazo = mapeamento_colunas['Prazo Rede']
        coluna_atp_osx = mapeamento_colunas['ATP/OSX']
        coluna_wcd = mapeamento_colunas['wcd']
        
        # Total de registros na base do sistema (adicionado para evitar KeyError)
        total_base = BaseConsolidada.objects.count()
        
        # Cria dicionários para dados da base externa
        dados_rede_por_pedido = {}
        dados_rede_por_atp_osx = {}
        dados_rede_por_wcd = {}
        
        # Processa os dados da base externa
        for _, row in df.iterrows():
            try:
                pedido = str(row[coluna_pedido]).strip() if pd.notnull(row[coluna_pedido]) else ""
                atp_osx = str(row[coluna_atp_osx]).strip() if pd.notnull(row[coluna_atp_osx]) else ""
                wcd = str(row[coluna_wcd]).strip() if pd.notnull(row[coluna_wcd]) else ""
                
                # Pula linhas sem identificadores
                if not pedido and not atp_osx and not wcd:
                    continue
                    
                # Converte a data, tratando possíveis erros
                data_rede = None
                if pd.notnull(row[coluna_prazo]):
                    try:
                        data_rede = pd.to_datetime(row[coluna_prazo]).date()
                    except Exception as e:
                        warnings.warn(f"Erro ao converter data do pedido {pedido}: {str(e)}")
                
                dados_pedido = {
                    'status_rede': str(row[coluna_analise]).strip() if pd.notnull(row[coluna_analise]) else None,
                    'eps_rede': str(row[coluna_contratada]).strip() if pd.notnull(row[coluna_contratada]) else None,
                    'data_rede': data_rede
                }
                
                # Armazena os dados por cada identificador
                if pedido:
                    dados_rede_por_pedido[pedido] = dados_pedido
                if atp_osx:
                    dados_rede_por_atp_osx[atp_osx] = dados_pedido
                if wcd:
                    dados_rede_por_wcd[wcd] = dados_pedido
                    
            except Exception as e:
                warnings.warn(f"Erro ao processar linha do pedido {row.get(coluna_pedido, 'DESCONHECIDO')}: {str(e)}")
                continue
        
        # Contadores para estatísticas
        atualizados_por_pedido = 0
        atualizados_por_atp_osx = 0
        atualizados_por_wcd = 0
        
        # Conjunto para rastrear pedidos já atualizados (evita atualizações duplicadas)
        pedidos_ja_atualizados = set()
        
        # Realiza as atualizações em uma única transação
        with transaction.atomic():
            # 1. Atualização por número de pedido
            for pedido, dados in dados_rede_por_pedido.items():
                try:
                    registros = BaseConsolidada.objects.filter(pedido=pedido)
                    if registros.exists():
                        registros.update(
                            status_rede=dados['status_rede'],
                            eps_rede=dados['eps_rede'],
                            data_rede=dados['data_rede']
                        )
                        atualizados_por_pedido += registros.count()
                        # Adiciona aos pedidos já atualizados
                        pedidos_ja_atualizados.add(pedido)
                except Exception as e:
                    warnings.warn(f"Erro ao atualizar por pedido {pedido}: {str(e)}")
                    continue
            
            # 2. Atualização por ATP/OSX
            for atp_osx, dados in dados_rede_por_atp_osx.items():
                try:
                    # Busca por num_atp ou osx, excluindo pedidos já atualizados
                    registros = BaseConsolidada.objects.filter(
                        Q(num_atp=atp_osx) | Q(osx=atp_osx)
                    ).exclude(
                        pedido__in=pedidos_ja_atualizados
                    )
                    
                    if registros.exists():
                        registros.update(
                            status_rede=dados['status_rede'],
                            eps_rede=dados['eps_rede'],
                            data_rede=dados['data_rede']
                        )
                        # Adiciona os pedidos atualizados ao conjunto
                        pedidos_atualizados = list(registros.values_list('pedido', flat=True))
                        pedidos_ja_atualizados.update(pedidos_atualizados)
                        atualizados_por_atp_osx += registros.count()
                except Exception as e:
                    warnings.warn(f"Erro ao atualizar por ATP/OSX {atp_osx}: {str(e)}")
                    continue
            
            # 3. Atualização por WCD
            for wcd, dados in dados_rede_por_wcd.items():
                try:
                    # Busca por wcd, excluindo pedidos já atualizados
                    registros = BaseConsolidada.objects.filter(
                        wcd=wcd
                    ).exclude(
                        pedido__in=pedidos_ja_atualizados
                    )
                    
                    if registros.exists():
                        registros.update(
                            status_rede=dados['status_rede'],
                            eps_rede=dados['eps_rede'],
                            data_rede=dados['data_rede']
                        )
                        atualizados_por_wcd += registros.count()
                except Exception as e:
                    warnings.warn(f"Erro ao atualizar por WCD {wcd}: {str(e)}")
                    continue
        
        total_atualizados = atualizados_por_pedido + atualizados_por_atp_osx + atualizados_por_wcd
        
        return {
            'total_rede': len(dados_rede_por_pedido),
            'total_base': total_base,
            'registros_com_atp_osx': len(dados_rede_por_atp_osx),
            'registros_com_wcd': len(dados_rede_por_wcd),
            'atualizados_por_pedido': atualizados_por_pedido,
            'atualizados_por_atp_osx': atualizados_por_atp_osx,
            'atualizados_por_wcd': atualizados_por_wcd,
            'total_atualizados': total_atualizados
        }
        
    except Exception as e:
        raise Exception(f"Erro ao atualizar rede externa: {str(e)}") 