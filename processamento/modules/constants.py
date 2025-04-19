# constants.py

from .utils import (
    mes_anterior,
    mes_corrente,
    mes_seguinte,
    mes_seguinte_2,
)

REPORT_COLUMNS = ['Pedido', 'Dias_CarteiraAtual', 'TM_Tec_Total', 'Num_WCD', 'Num_ATP',
                    'Classificacao_Resumo_Atual', 'SegResumo', 'Quebra_Esteira', 'Esteira', 'Esteira_Regionalizada', 'Segmento_V3',
                    'Carteira', 'Cliente', 'Cidade', 'OSX', 'Cadeia_Pendencias_Descricao', 'DataTecnica', 'Produto',
                    'Servico', 'Delta_REC_LIQ', 'Tecnologia_Report', 'Aging Resumo', 'Projetos', 'Projetos_Lote',
                    'Motivo_PTA_Cod', 'Origem Pend.', 'SLA_TECNICA', 'DraftEncontrado', 'TarefaAtualDraft', 'DataCriaçãoDraft']

REDE_COLUMNS = ['PEDIDO', 'ANALISE 02', 'CONTRATADA', 'Prazo Rede']

DATATABLE_COLUMNS = ['Pedido', 'Dias_CarteiraAtual', 'DataTecnica', 'Carteira', 'Pendencia_Macro', 'Estimativa']

CADEIAS_VISTORIA = ['Aguardar Vistoria', 'Agendar Vistoria', 'Analisar resultado do Survey', 'Análise e Vistoria Rede Interna', \
                'Informar Agenda de Vistoria', 'Vistoria Agendada(Gov)']

CADEIAS_INFRA = ['Anexar Laudo de Infra e Elaborar Orçamento T2', 'Revisar Laudo de Infra e T2', 'Aguardar execução de obra de infra']

REDE_VISTORIA = ['AGENDAR VISTORIA']

REDE_OK = ['REDE OK']

REDE_QUEBRA = "QUEBRA - NÃO ENTREGUE"

CARTEIRAS_CENTRALIZADO = ['Viabilidade', 'Planejamento', 'TI']

CARTEIRAS_VISTORIA = ['Vistoria']

CARTEIRAS_ATIVACAO = ['Ativação', 'Implantação', 'Metro-Config', 'Transporte', 'Engenharia']

CARTEIRAS_MATERIAL = ['Material']

CARTEIRAS_REDE = ['Rede']

CARTEIRAS_REGIONAL = CARTEIRAS_VISTORIA + CARTEIRAS_REDE + CARTEIRAS_ATIVACAO + CARTEIRAS_MATERIAL

NAO_REDE = ['REDE ENTREGUE', 'NÃO ENVOLVE REDE', 'CANCELADA', 'RÁDIO', '-', '']

REDE_MES_FUTURO = ['MANUTENÇÃO', 'PROJETO', 'REABERTO', 'EM APROVAÇÃO DRAFT', 'CONCESSIONARIA', \
    'PLANEJAMENTO', 'FORA DE PREMISSA', 'PARALIZADO', 'ACESSO', 'INFRA VIVO', 'CADASTRAR', \
    'ULTIMO DU', 'IMPORTADO_SN', 'IMPORTADO_REPORT', mes_seguinte(), mes_seguinte_2()]

REDE_MES_CORRENTE = ['DATAR', mes_corrente(), mes_anterior(), REDE_QUEBRA]

PCC_PROPENSOS = ['DATAR', mes_anterior(), mes_corrente(), mes_seguinte(), mes_seguinte_2(), REDE_QUEBRA, 'MANUTENÇÃO', \
    'PROJETO', 'REABERTO', 'EM APROVAÇÃO DRAFT', 'CONCESSIONARIA', 'CADASTRAR', 'ULTIMO DU', REDE_QUEBRA]

PENDENCIA_PADRAO = 'Agendado/Em agendamento'

# Constantes para tags de dias_carteira
DIAS_CARTEIRA_ALERTA = 7  # Número de dias para alerta laranja
DIAS_CARTEIRA_CRITICO = 14  # Número de dias para alerta vermelho

# Constantes para status de pedidos
PENDENCIAS_MACRO = [
    'Agendado/Em Agendamento',
    'Retorno PCC/Planejamento - Revisar'
]

# Constantes para classificação
CLASSIFICACAO_TECNICA = 'Tecnica'
ESTEIRA_PE = 'PE'

# Lista completa de valores distintos de pendencia_macro
PENDENCIAS_MACRO_OPCOES = [
    "Agendado/Em Agendamento",
    "Cancelado",
    "Centralizado/Planejamento",
    "Entregue",
    "Infra/Bloqueio GB/Plataforma",
    "Engenharia/Rede IP/Transporte",
    "Capacitação/Filiação",
    "DWDM/SWT Grande Porte"
    "PABX Pendente",
    "Pend Cliente/Comercial",
    "Rede Externa",
    "SIP/PABX - Agendar",
    "Retorno PCC/Planejamento - Revisar",
    "Sem ETP emitido - Devolver",
    "VGR - Agendar",
    "Vistoria"
]