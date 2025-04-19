# business_rules.py
import pandas as pd
import numpy as np

# Imports from custom modules

from .classification import (
    validar_data_tecnica,
    estimativa_sae,
    ajustar_esteira,
    ajustar_rede_cadastrar,
    classificar_entrega,
    classificar_corporate,
    calcula_quebra,
    ajustar_rede_pcc_completo,
    ajustar_estimativa_quebra,
    ajustar_estimativa_datar,
    ajustar_ultimo_du,
    ajustar_projeto,
)

from .constants import (
    CARTEIRAS_CENTRALIZADO,
    CARTEIRAS_VISTORIA,
    CARTEIRAS_ATIVACAO,
    CARTEIRAS_MATERIAL,
    CARTEIRAS_REDE,
    CARTEIRAS_REGIONAL,
    CADEIAS_INFRA,
    REDE_OK,
    REDE_MES_FUTURO,
    REDE_MES_CORRENTE,
    NAO_REDE,
    PENDENCIA_PADRAO,
)

CRITERIA_MATRIX = [

    # Priority: seguir a ordem das cartei, e ordem das epecificades (ex. Centralizado iniciar marcado os PE Sem ETP e com ETP emitido a serem avaliados, depois tudo o que se encontra em carteiras do centralizado)

    {
        "priority": 10, # All - Cancelado
        "conditions": {
            "classificacao_resumo_atual": "Cancelado",
        },
        "agrupado": "Cancelado",
        "status_macro": "Cancelado",
        "ativacao": "Agenda Futura",
    },  

    {
        "priority": 20, # All - Faturado
        "conditions": {
            "classificacao_resumo_atual": ["Falta RFB", "Faturado"],
        },
        "agrupado": "Entregue",
        "status_macro": "Entregue",
        "ativacao": "Agenda Mês",
    },  
    
    {
        "priority": 30, # All - Pend Cliente / Comercial
        "conditions": {
            "classificacao_resumo_atual": "Pend Cliente / Comercial",
        },
        "agrupado": "PCC",
        "status_macro": "Pend Cliente/Comercial",
        "ativacao": "Agenda Futura",
    },  
    
    {
        "priority": 40, # PE - Sem ETP emitido nas filas da Tecnica
        "conditions": {
            "esteira": "PE",
            "classificacao_resumo_atual": "Tecnica",
            "num_atp": lambda x: x is None or x == "" or pd.isna(x),
        },
        "agrupado": "Centralizado - Emissão",
        "status_macro": "Sem ETP emitido - Devolver",
        "ativacao": "Agenda Futura",
    },

    {
        "priority": 50, # PE - Carteira Planejamento c/ ETP emitido, Cadeia_Pendencias_Descricao = Efetuar Ajustes
        "conditions": {
            "esteira": "PE",
            "carteira": "Planejamento",
            "num_atp": lambda x: isinstance(x, str) and x.strip() != "" and not pd.isna(x),
            "cadeia_pendencias_descricao": "Efetuar ajustes",
        },
        "agrupado": "Centralizado - Emissão",
        "status_macro": "Centralizado/Planejamento",
        "ativacao": "Agenda Futura",
    },  

    {
        "priority": 60, # PE - Carteira Planejamento c/ ETP emitido, Status_Rede = PLANEJAMENTO
        "conditions": {
            "esteira": "PE",
            "carteira": CARTEIRAS_REGIONAL,
            "num_atp": lambda x: isinstance(x, str) and x.strip() != "" and not pd.isna(x),
            "status_rede": "PLANEJAMENTO",
        },
        "agrupado": "Retorno PCC/Planejamento - Revisar",
        "status_macro": "Retorno PCC/Planejamento - Revisar",
        "ativacao": "Agenda Futura",
    },  

    {
        "priority": 70, # PE - Viabilidade c/ ETP emitido, marcar p/ avaliação pela gestão
        "conditions": {
            "esteira": "PE",
            "carteira": "Viabilidade",
            "num_atp": lambda x: isinstance(x, str) and x.strip() != "" and not pd.isna(x),
            # "status_rede": NAO_REDE,
        },
        "agrupado": "Retorno PCC/Planejamento - Revisar",
        "status_macro": "Retorno PCC/Planejamento - Revisar",
        "ativacao": "Agenda Futura",
    },  
    
    {
        "priority": 80, # All - Tudo o mais nas carteiras Centralizado/Planejamento
        "conditions": {
            "carteira": CARTEIRAS_CENTRALIZADO,
            "status_rede": NAO_REDE,
        },
        "agrupado": "Centralizado - Emissão",
        "status_macro": "Centralizado/Planejamento",
        "ativacao": "Agenda Futura",
    },

    {
        "priority": 90, # All - Rede Futura (Status_Rede)
        "conditions": {
            "carteira": CARTEIRAS_REGIONAL,
            "status_rede": REDE_MES_FUTURO,
        },
        "agrupado": "Rede Externa",
        "status_macro": "Rede Externa",
        "ativacao": "Agenda Futura",
    },
    
    {
        "priority": 100, # All - Rede Mês (Status_Rede)
        "conditions": {
            "carteira": CARTEIRAS_REGIONAL,
            "status_rede": REDE_MES_CORRENTE,
        },
        "agrupado": "Rede Externa",
        "status_macro": "Rede Externa",
        "ativacao": "Agenda Mês",
    },
    
    {
        "priority": 110, # All - Vistoria (Status_Rede)
        "conditions": {
            "status_rede": ["AGENDAR VISTORIA"],
        },
        "agrupado": "Vistoria",
        "status_macro": "Vistoria",
        "ativacao": "Agenda Futura",
    },
    
    {
        "priority": 120, # All - Vistoria (Carteira)
        "conditions": {
            "carteira": CARTEIRAS_VISTORIA,
        },
        "agrupado": "Vistoria",
        "status_macro": "Vistoria",
        "ativacao": "Agenda Futura",
    },
    
    {
        "priority": 130, # All - Infra (Cadeia_Pendencias_Descricao)
        "conditions": {
            "cadeia_pendencias_descricao": CADEIAS_INFRA,
        },
        "agrupado": "Vistoria",
        "status_macro": "Infra/Bloqueio GB/Plataforma",
        "ativacao": "Agenda Mês",
    },
    
    {
        "priority": 140, # All - VGR (Cadeia_Pendencias_Descricao)
        "conditions": {
            "esteira": "EC",       
            "servico": "VIVO GESTÃO DE REDES",
            "carteira": CARTEIRAS_ATIVACAO + CARTEIRAS_CENTRALIZADO,
        },
        "agrupado": "Agendado/Em Agendamento",
        "status_macro": "VGR - Agendar",
        "ativacao": "Agenda Mês",
    },

    {
        "priority": 150, # All - VGR (Cadeia_Pendencias_Descricao)
        "conditions": {
            "esteira": "PE",       
            "servico": "VIVO GESTÃO DE REDES",
            "carteira": CARTEIRAS_ATIVACAO + CARTEIRAS_CENTRALIZADO,
        },
        "agrupado": "Agendado/Em Agendamento",
        "status_macro": "Agendado/Em Agendamento",
        "ativacao": "Agenda Mês",
    },

    {
        "priority": 160, # PE - Pedidos SIP em PCC no Remedy
        "conditions": {
            "esteira": "PE",
            "servico": "VIVO SIP",
            "classificacao_resumo_atual": "Tecnica",
            "motivo_pta_cod": lambda x: isinstance(x, int) and x == 7918,
        },
        "agrupado": "Agendado/Em Agendamento",
        "status_macro": "SIP em PCC no Remedy - Tramitar PCC",
        "ativacao": "Agenda Mês",
    },

    {
        "priority": 170, # PE - SIP, PE ,s/ dependencia de reede alocados na carteira de Falta de Material
        "conditions": {
            "esteira": "PE",
            "servico": "VIVO SIP",
            "carteira": CARTEIRAS_MATERIAL,
        },
        "agrupado": "Agendado/Em Agendamento",
        "status_macro": "SIP - Agendar",
        "ativacao": "Agenda Mês",
    },
    
    {
        "priority": 180, # EC - SIP, PE ,s/ dependencia de reede alocados na carteira de Falta de Material
        "conditions": {
            "esteira": "EC",
            "servico": "VIVO SIP",
            "carteira": CARTEIRAS_MATERIAL,
        },
        "agrupado": "Agendado/Em Agendamento",
        "status_macro": "PABX Pendente",
        "ativacao": "Agenda Mês",
    },
    
    {
        "priority": 190, # All - Direciona tudo que estiver na Ativação ou Rede, sem dependencia de Rede Externa, p/ Agendamento
        "conditions": {
            "carteira": CARTEIRAS_ATIVACAO + CARTEIRAS_REDE + CARTEIRAS_VISTORIA,
            "status_rede": REDE_OK,
        },
        "agrupado": PENDENCIA_PADRAO,
        "status_macro": PENDENCIA_PADRAO,
        "ativacao": "Agenda Mês",
    },

    # Outras regras conforme necessário...
]

def classify_record(record, criteria_matrix, pendencia_padrao):
    """
    Classifica um registro de acordo com a matriz de critérios.
    Retorna sempre valores válidos para agrupado, pendencia_macro e estimativa.
    """
    try:
        # Itera pelas regras na ordem de prioridade
        for rule in sorted(criteria_matrix, key=lambda r: r["priority"]):
            # Verifica cada condição da regra
            if all(
                (record[col] in cond if isinstance(cond, list) else  # Verifica lista com "IN"
                 cond(record[col]) if callable(cond) else  # Verifica condição lambda
                 record[col] == cond)  # Verifica igualdade simples
                for col, cond in rule["conditions"].items()
            ):
                # Retorna os campos se a regra foi satisfeita
                return {
                    "agrupado": rule["agrupado"] if rule["agrupado"] else pendencia_padrao,
                    "pendencia_macro": rule["status_macro"] if rule["status_macro"] else pendencia_padrao,
                    "estimativa": rule["ativacao"] if rule["ativacao"] else "Agenda Mês"
                }
    except Exception as e:
        print(f"Erro ao classificar registro: {str(e)}")
        print(f"Registro: {record.to_dict()}")
    
    # Retorno padrão se nenhuma regra for atendida ou ocorrer erro
    return {
        "agrupado": pendencia_padrao,
        "pendencia_macro": pendencia_padrao,
        "estimativa": "Agenda Mês"
    }

def processar_regras_negocio(df):
    """
    Processa regras de negócio para classificação e agrupamento de pedidos
    """
    try:
        print("Iniciando processamento das regras de negócio...")
        print(f"Total de registros a processar: {len(df)}")
        print(f"Colunas disponíveis: {df.columns.tolist()}")
        
        # Verificar se a coluna pedido existe e criar uma cópia do dataframe original
        df_original = df.copy()
        
        # Se pedido não estiver no dataframe, usar o índice atual ou criar um novo
        if 'pedido' not in df.columns:
            # Se o índice atual não for o padrão (RangeIndex), use-o como pedido
            if not isinstance(df.index, pd.RangeIndex):
                df['pedido'] = df.index
            else:
                # Caso contrário, use o id como pedido
                if 'id' in df.columns:
                    df['pedido'] = df['id']
                else:
                    # Ou crie um novo ID sequencial como último recurso
                    df['pedido'] = [f"AUTO_{i}" for i in range(len(df))]
        
        # Agora podemos definir o índice com segurança
        df = df.set_index('pedido')
        print("Índice definido como 'pedido'")
        
        # Remove linhas onde "esteira" está vazio ou NaN
        print("Removendo linhas com esteira vazia...")
        df = df[df["esteira"].notna() & (df["esteira"] != "")]
        print(f"Total de registros após remoção: {len(df)}")

        print("Aplicando transformações iniciais...")
        # Aplicar transformações iniciais
        try:
            df.loc[:, 'tipo_entrega'] = df.apply(classificar_entrega, axis=1)
            print("tipo_entrega aplicado")
            
            df.loc[:, 'esteira'] = df.apply(ajustar_esteira, axis=1)
            print("esteira ajustada")
            
            df.loc[:, 'segmento_v3'] = df.apply(classificar_corporate, axis=1)
            print("segmento_v3 classificado")
        except Exception as e:
            print(f"Erro nas transformações iniciais: {str(e)}")
            raise

        print("Aplicando transformações de status_rede...")
        try:
            df.loc[:, 'status_rede'] = df.apply(calcula_quebra, axis=1)
            df.loc[:, "status_rede"] = df.apply(ajustar_rede_cadastrar, axis=1)
            df.loc[:, "status_rede"] = df.apply(ajustar_ultimo_du, axis=1)
            df.loc[:, "status_rede"] = df.apply(ajustar_projeto, axis=1)
            print("status_rede atualizado")
        except Exception as e:
            print(f"Erro nas transformações de status_rede: {str(e)}")
            raise

        print("Aplicando classificação geral...")
        try:
            # Aplica a classificação para cada registro
            for idx, row in df.iterrows():
                resultado = classify_record(row, CRITERIA_MATRIX, PENDENCIA_PADRAO)
                df.at[idx, 'agrupado'] = resultado['agrupado']
                df.at[idx, 'pendencia_macro'] = resultado['pendencia_macro']
                df.at[idx, 'estimativa'] = resultado['estimativa']
            
            print("Classificação geral aplicada")

            df.loc[:, 'data_sae'] = df.apply(estimativa_sae, axis=1)
            print("data_sae aplicado")
            

        except Exception as e:
            print(f"Erro na classificação geral: {str(e)}")
            raise

        print("Ajustando estimativas...")
        try:
            df.loc[:, 'estimativa'] = df.apply(ajustar_estimativa_quebra, axis=1)
            df.loc[:, 'estimativa'] = df.apply(ajustar_estimativa_datar, axis=1)
            print("Estimativas ajustadas")
        except Exception as e:
            print(f"Erro no ajuste de estimativas: {str(e)}")
            raise

        # Contabilizar atualizações
        total_atualizados = len(df)
        print(f"Total de registros atualizados: {total_atualizados}")
        print(f"Colunas finais: {df.columns.tolist()}")
        print(f"Exemplo de dados: {df.iloc[0].to_dict()}")

        return {
            'success': True,
            'df_atualizado': df,
            'resultados': {
                'total_atualizados': total_atualizados
            }
        }
    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Traceback completo: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }
