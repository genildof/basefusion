# utils.py
from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale

# Definir a localidade para português do Brasil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except locale.Error:
            # Fallback para o locale padrão se nenhum dos anteriores funcionar
            locale.setlocale(locale.LC_TIME, '')
            print("Atenção: Não foi possível configurar o locale para português brasileiro. Usando locale padrão.")

# Função para obter o nome do mês seguinte
def mes_seguinte():
    hoje = datetime.now()
    proximo_mes = hoje + relativedelta(months=+1)
    return proximo_mes.strftime("%B").upper()

# Função para obter o nome do mês seguinte
def mes_seguinte_2():
    hoje = datetime.now()
    proximo_mes = hoje + relativedelta(months=+2)
    return proximo_mes.strftime("%B").upper()

# Função para obter o nome do mês anterior
def mes_anterior():
    hoje = datetime.now()
    mes_passado = hoje - relativedelta(months=1)
    return mes_passado.strftime("%B").upper()

# Função para obter o nome do mês corrente
def mes_corrente():
    hoje = datetime.now()
    return hoje.strftime("%B").upper()