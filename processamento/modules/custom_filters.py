FILTROS = {
    'revisar': {
        'pendencia_macro': ['Agendado/Em agendamento', 'Retorno PCC/Planejamento - Revisar'],
        'classificacao_resumo_atual': 'Tecnica',
        'esteira': 'PE'
    },
    'tecnica': {
        'classificacao_resumo_atual': 'Tecnica',
    },
    'todos': {}
}

def get_filtro(tipo):
    """
    Retorna o dicionário de filtros para o tipo especificado.
    Se o tipo não existir, retorna um dicionário vazio.
    """
    return FILTROS.get(tipo, {}) 