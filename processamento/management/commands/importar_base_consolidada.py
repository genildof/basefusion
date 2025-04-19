from django.core.management.base import BaseCommand
import pandas as pd
from processamento.models import BaseConsolidada
import warnings
from datetime import datetime
import numpy as np

class Command(BaseCommand):
    help = 'Importa dados da base consolidada do Excel'

    def handle(self, *args, **options):
        try:
            # Ler o arquivo Excel da aba Base_Consolidada
            df = pd.read_excel('base_batimento_report_17_04_10_20.xlsx', sheet_name='Base_Consolidada')
            
            # Mostrar as colunas disponíveis
            self.stdout.write(self.style.SUCCESS('Colunas disponíveis no arquivo:'))
            for coluna in df.columns:
                self.stdout.write(f'- {coluna}')
            
            # Verificar se as colunas necessárias existem
            colunas_necessarias = [
                'Pedido', 'Cliente', 'Cidade', 'Esteira', 'Esteira_Regionalizada',
                'SegResumo', 'Produto', 'Servico', 'Classificacao_Resumo_Atual',
                'Cadeia_Pendencias_Descricao', 'Carteira', 'Dias_CarteiraAtual',
                'DataTecnica', 'OSX', 'Motivo_PTA_Cod', 'Num_WCD', 'Num_ATP',
                'DraftEncontrado', 'DataCriaçãoDraft', 'TarefaAtualDraft',
                'Tecnologia_Report', 'Quebra_Esteira', 'Projetos', 'Projetos_Lote',
                'TM_Tec_Total', 'Delta_REC_LIQ', 'Aging Resumo', 'Origem Pend.',
                'Segmento_V3', 'SLA_TECNICA', 'Status_Rede', 'EPS_Rede', 'Data_Rede',
                'Tipo_Entrega', 'Data_SAE', 'Agrupado', 'Pendencia_Macro', 'Estimativa'
            ]
            
            colunas_faltantes = [coluna for coluna in colunas_necessarias if coluna not in df.columns]
            if colunas_faltantes:
                self.stdout.write(self.style.ERROR(f'Colunas não encontradas no arquivo Excel: {", ".join(colunas_faltantes)}'))
                return
            
            # Substituir NaN por None
            df = df.replace({np.nan: None})
            
            # Contadores
            total_importados = 0
            total_erros = 0
            
            def converter_data(valor, nome_campo, pedido):
                if pd.isna(valor) or valor is None:
                    return None
                
                # Se o valor for uma string que não parece ser uma data
                if isinstance(valor, str) and not any(c.isdigit() for c in valor):
                    return None
                
                try:
                    return pd.to_datetime(valor).date()
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Erro ao converter {nome_campo} para pedido {pedido}: {str(e)}'))
                    return None
            
            # Iterar sobre as linhas do DataFrame
            for index, row in df.iterrows():
                try:
                    # Converter datas
                    data_tecnica = converter_data(row['DataTecnica'], 'data técnica', row['Pedido'])
                    data_criacao_draft = converter_data(row['DataCriaçãoDraft'], 'data criação draft', row['Pedido'])
                    data_rede = converter_data(row['Data_Rede'], 'data rede', row['Pedido'])
                    data_sae = converter_data(row['Data_SAE'], 'data sae', row['Pedido'])
                    
                    # Criar ou atualizar registro
                    BaseConsolidada.objects.update_or_create(
                        pedido=row['Pedido'],
                        defaults={
                            'cliente': row['Cliente'],
                            'cidade': row['Cidade'],
                            'esteira': row['Esteira'],
                            'esteira_regionalizada': row['Esteira_Regionalizada'],
                            'seg_resumo': row['SegResumo'],
                            'produto': row['Produto'],
                            'servico': row['Servico'],
                            'classificacao_resumo_atual': row['Classificacao_Resumo_Atual'],
                            'cadeia_pendencias_descricao': row['Cadeia_Pendencias_Descricao'],
                            'carteira': row['Carteira'],
                            'dias_carteira_atual': row['Dias_CarteiraAtual'],
                            'data_tecnica': data_tecnica,
                            'osx': row['OSX'],
                            'motivo_pta_cod': row['Motivo_PTA_Cod'],
                            'wcd': row['Num_WCD'],
                            'num_atp': row['Num_ATP'],
                            'draft_encontrado': row['DraftEncontrado'],
                            'data_criacao_draft': data_criacao_draft,
                            'tarefa_atual_draft': row['TarefaAtualDraft'],
                            'tecnologia_report': row['Tecnologia_Report'],
                            'quebra_esteira': row['Quebra_Esteira'],
                            'projetos': row['Projetos'],
                            'projetos_lote': row['Projetos_Lote'],
                            'tm_tec_total': row['TM_Tec_Total'],
                            'delta_rec_liq': row['Delta_REC_LIQ'],
                            'aging_resumo': row['Aging Resumo'],
                            'origem_pend': row['Origem Pend.'],
                            'segmento_v3': row['Segmento_V3'],
                            'sla_tecnica': row['SLA_TECNICA'],
                            'status_rede': row['Status_Rede'],
                            'eps_rede': row['EPS_Rede'],
                            'data_rede': data_rede,
                            'tipo_entrega': row['Tipo_Entrega'],
                            'data_sae': data_sae,
                            'agrupado': row['Agrupado'],
                            'pendencia_macro': row['Pendencia_Macro'],
                            'estimativa': row['Estimativa']
                        }
                    )
                    total_importados += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Erro ao importar pedido {row["Pedido"]}: {str(e)}'))
                    total_erros += 1
            
            self.stdout.write(self.style.SUCCESS(f'Importação concluída! Total de registros importados: {total_importados}, Total de erros: {total_erros}'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Arquivo base_batimento_report_17_04_10_20.xlsx não encontrado!'))
        except ValueError:
            self.stdout.write(self.style.ERROR('Aba Base_Consolidada não encontrada no arquivo!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar dados: {str(e)}')) 