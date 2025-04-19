# classification.py
import pandas as pd
import re

from datetime import datetime, timedelta

from .utils import (
    mes_corrente, 
    mes_anterior,
)

from .constants import (
    REDE_OK,
    REDE_QUEBRA,
    REDE_MES_CORRENTE,
    PCC_PROPENSOS,
)

# Classificar os pedidos como físicos e não físicos ou atacado, coluna Tipo_Entrega
def classificar_entrega(row):
    if row['projetos'] == "FUST":
        return 'FUST'
    elif row['produto'] == "DADOS":
        if row['segmento_v3'] == "ATACADO":
            return 'Atacado'
        else:
            return 'Físico'
    else:
        return 'Não Físico'

# Classificar os pedidos indevidamente marcados como Corporate, co
def classificar_corporate(row):
    if row['segmento_v3'] == "Corporate":
        return 'ISE'
    else:
        return row['segmento_v3']
        
def validar_data_tecnica(row):
    """
    Valida e formata a data técnica.
    Retorna a data formatada como string no formato DD/MM/YYYY ou None se inválida.
    """
    try:
        if pd.isna(row["data_tecnica"]) or row["data_tecnica"] == "":
            return None
            
        # Se já for uma string no formato correto, retorna
        if isinstance(row["data_tecnica"], str) and len(row["data_tecnica"]) == 10:
            return row["data_tecnica"]
            
        # Converte para datetime se necessário
        if isinstance(row["data_tecnica"], (pd.Timestamp, datetime)):
            return row["data_tecnica"].strftime("%d/%m/%Y")
            
        # Tenta converter string para datetime
        try:
            data = pd.to_datetime(row["data_tecnica"])
            return data.strftime("%d/%m/%Y")
        except:
            return None
            
    except Exception as e:
        print(f"Erro ao validar data técnica: {str(e)}")
        return None

def estimativa_sae(row):
    """Estima o status SAE com base na data técnica e estimativa"""
    invalido = "Ajustar SAE"

    try:
        # Verifica se há data técnica
        if pd.isna(row['data_tecnica']) or row['data_tecnica'] == '':
            return invalido
            
        # Tenta converter a data técnica para datetime
        try:
            # Tenta primeiro o formato com hora
            dt = datetime.strptime(str(row['data_tecnica']), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Se falhar, tenta o formato sem hora
                dt = datetime.strptime(str(row['data_tecnica']), '%Y-%m-%d')
            except ValueError:
                return invalido

        data_atual = datetime.now()
        mes_atual = data_atual.month
        ano_atual = data_atual.year
        
        # Verifica se a estimativa é Agenda Futura
        if row['estimativa'] == 'Agenda Futura':
            # Para Agenda Futura, só considera OK se a data for do mês seguinte em diante
            if dt.year > ano_atual or (dt.year == ano_atual and dt.month > mes_atual):
                return "OK"
            else:
                return invalido
                
        # Verifica se a estimativa é Agenda Mês
        elif row['estimativa'] == 'Agenda Mês':
            # Se a data for do mês atual
            if dt.year == ano_atual and dt.month == mes_atual:
                # Verifica se é dia útil (não é sábado nem domingo)
                if dt.weekday() < 5:  # 0-4 = segunda a sexta
                    # Verifica se é do dia seguinte até o último dia do mês
                    if dt.day > data_atual.day:
                        return "OK"
                    else:
                        return invalido
                else:
                    return invalido
            else:
                return invalido
                
        # Para outras estimativas, retorna inválido
        else:
            return invalido
            
    except Exception as e:
        print(f"Erro ao estimar SAE: {str(e)}")
        return invalido
    
def ajustar_esteira(row):
    # Verifica se esteira é "EC" e num_atp está no padrão desejado
    if row["esteira"] == "EC" and isinstance(row["num_atp"], str) and \
        re.match(r'\w{4}/\w{2}', row["num_atp"]) and row["num_atp"] != "0000/00":
        return "PE"
    else:
        return row["esteira"]
        

def ajustar_rede_pcc_completo(row):
    """
    Função unificada para ajustes de rede PCC, combinando as lógicas de ajustar_rede_pcc e ajustar_rede_ok_pcc
    """
    # Condições comuns
    condicoes_base = (
        row.get("esteira") == "PE" and
        row.get("classificacao_resumo_atual") == "Pend Cliente / Comercial" and
        row.get("projetos") != "FUST"
    )
    
    if not condicoes_base:
        return (
            row.get("classificacao_resumo_atual", ""), 
            row.get("carteira", ""), 
            row.get("sla_tecnica", "")
        )
    
    # SLA técnica ajustada
    sla_tecnica = "Propenso" if row.get("sla_tecnica") == "Atrasado" else row.get("sla_tecnica", "")
    
    # Verifica primeiro as condições para REDE_OK
    if (row.get("status_rede") in REDE_OK and row.get("dias_carteira_atual", 0) < 100):
        return "Tecnica", "Ativação", sla_tecnica
    
    # Verifica as condições para PCC_PROPENSOS
    if row.get("status_rede") in PCC_PROPENSOS:
        return "Tecnica", "Rede", sla_tecnica
    
    # Retorna valores originais se nenhuma condição for atendida
    return (
        row.get("classificacao_resumo_atual", ""), 
        row.get("carteira", ""), 
        row.get("sla_tecnica", "")
    )

def ajustar_rede_cadastrar(row):
    # Verifica condição base comum
    if row["carteira"] != "Rede" or not (pd.isna(row["status_rede"]) or row["status_rede"] == ""):
        return row["status_rede"]
    
    # Verifica condições específicas
    if (row["esteira"] == "EC" or 
        (row["esteira"] == "PE" and 
         isinstance(row["num_atp"], str) and 
         row["num_atp"].strip())):
        return "CADASTRAR"
    
    return row["status_rede"]

def calcula_quebra(row):
    # Armazena os valores de mes_anterior() e mes_corrente() para evitar chamadas repetidas
    meses_validos = {mes_anterior(), mes_corrente()}
    
    # Verifica se o status_rede está fora dos meses válidos
    if row["status_rede"] not in meses_validos:
        return row['status_rede']
    
    try:
        # Converte a data_rede para um objeto datetime
        date_rede = datetime.strptime(str(row['data_rede']), '%Y-%m-%d %H:%M:%S')
        data_atual = datetime.now()
        
        # Verifica se a data é anterior à data atual menos 1 dia
        if date_rede < (data_atual - timedelta(days=1)):
            return REDE_QUEBRA  # Data é menor que a data atual
        
    except (ValueError, TypeError):
        # Em caso de erro na conversão ou tipo inválido, retorna o status_rede
        pass
    
    # Retorna o status_rede se a data for válida ou se ocorrer uma exceção
    return row['status_rede']
        
def ajustar_estimativa_quebra(row):
    # Verifica se status_rede é None ou vazio
    if pd.isna(row["status_rede"]) or row["status_rede"] == "":
        return row["estimativa"]
        
    # Verifica se status_rede está em REDE_QUEBRA
    if row["status_rede"] in REDE_QUEBRA:
        if datetime.now().day > 29:
            return "Agenda Futura"
        else:
            return "Agenda Mês"
    else:
        return row["estimativa"]
        
def ajustar_estimativa_datar(row):
    # Verifica se status_rede é None ou vazio
    if pd.isna(row["status_rede"]) or row["status_rede"] == "":
        return row["estimativa"]
        
    if row['status_rede'] == "DATAR":
        # Obtém o dia atual do mês
        dia_atual = datetime.now().day
        
        # Retorna "Agenda Mês" se o dia for 20 ou menor
        if dia_atual <= 30:
            return "Agenda Mês"
        # Retorna "Agenda Futura" se o dia for maior que 20
        else:
            return "Agenda Futura"
    else:
        return row['estimativa']
        
def ajustar_projeto(row):
    return "PROJETO" if row['status_rede'] in ['PROJETO ENTREGUE', 'projeto'] else row['status_rede']


def ajustar_ultimo_du(row):
    try:
        # Retorna imediatamente se não estiver nos status elegíveis
        if not row["status_rede"] in REDE_MES_CORRENTE:
            return row["status_rede"]

        # Converte a data se necessário
        data = pd.to_datetime(row["data_rede"]) if isinstance(row["data_rede"], str) else row["data_rede"]
        
        # Determina o último dia do mês
        ultimo_dia_mes = (data.replace(day=1) + pd.offsets.MonthEnd(0)).date()
        
        # Retorna se não for o último dia do mês
        if data.date() != ultimo_dia_mes:
            return row["status_rede"]

        # Cria um range de datas do dia atual até o fim do mês
        dias_restantes = pd.date_range(data, ultimo_dia_mes)
        
        # Filtra apenas os dias úteis (weekday < 5)
        dias_uteis_restantes = [d for d in dias_restantes if d.weekday() < 5]
        
        # É último dia útil se for o único dia útil restante
        return "ULTIMO DU" if len(dias_uteis_restantes) == 1 else row["status_rede"]

    except Exception:
        return row["status_rede"]