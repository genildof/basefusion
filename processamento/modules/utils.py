# utils.py
from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale

# Dicionário de nomes de meses em português para não depender do locale
MESES_PT = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO", 
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO"
}

# Função para obter o nome do mês seguinte
def mes_seguinte():
    hoje = datetime.now()
    proximo_mes = hoje + relativedelta(months=+1)
    mes = proximo_mes.month
    return MESES_PT[mes]

# Função para obter o nome do mês seguinte
def mes_seguinte_2():
    hoje = datetime.now()
    proximo_mes = hoje + relativedelta(months=+2)
    mes = proximo_mes.month
    return MESES_PT[mes]

# Função para obter o nome do mês anterior
def mes_anterior():
    hoje = datetime.now()
    mes_passado = hoje - relativedelta(months=1)
    mes = mes_passado.month
    return MESES_PT[mes]

# Função para obter o nome do mês corrente
def mes_corrente():
    hoje = datetime.now()
    mes = hoje.month
    return MESES_PT[mes]