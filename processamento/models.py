from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Modelo para perfil de usuário
class PerfilUsuario(models.Model):
    PERFIL_CHOICES = [
        ('SUPERVISOR', 'Supervisor'),
        ('OPERADOR', 'Operador'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='OPERADOR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_perfil_display()}"
    
    @property
    def is_supervisor(self):
        return self.perfil == 'SUPERVISOR'
    
    @property
    def is_operador(self):
        return self.perfil == 'OPERADOR'

class BaseConsolidada(models.Model):
    pedido = models.CharField(max_length=50, unique=True)
    cliente = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=255, null=True, blank=True)
    esteira = models.CharField(max_length=255, null=True, blank=True)
    esteira_regionalizada = models.CharField(max_length=255, null=True, blank=True)
    seg_resumo = models.CharField(max_length=255, null=True, blank=True)
    produto = models.CharField(max_length=255, null=True, blank=True)
    servico = models.CharField(max_length=255, null=True, blank=True)
    classificacao_resumo_atual = models.CharField(max_length=255, null=True, blank=True)
    cadeia_pendencias_descricao = models.CharField(max_length=255, null=True, blank=True)
    carteira = models.CharField(max_length=255, null=True, blank=True)
    dias_carteira_atual = models.IntegerField(null=True, blank=True)
    data_tecnica = models.DateField(null=True, blank=True)
    osx = models.CharField(max_length=255, null=True, blank=True)
    motivo_pta_cod = models.CharField(max_length=255, null=True, blank=True)
    wcd = models.CharField(max_length=255, null=True, blank=True)
    num_atp = models.CharField(max_length=255, null=True, blank=True)
    draft_encontrado = models.CharField(max_length=255, null=True, blank=True)
    data_criacao_draft = models.DateField(null=True, blank=True)
    tarefa_atual_draft = models.CharField(max_length=255, null=True, blank=True)
    tecnologia_report = models.CharField(max_length=255, null=True, blank=True)
    quebra_esteira = models.CharField(max_length=255, null=True, blank=True)
    projetos = models.CharField(max_length=255, null=True, blank=True)
    projetos_lote = models.CharField(max_length=255, null=True, blank=True)
    tm_tec_total = models.CharField(max_length=255, null=True, blank=True)
    delta_rec_liq = models.CharField(max_length=255, null=True, blank=True)
    aging_resumo = models.CharField(max_length=255, null=True, blank=True)
    origem_pend = models.CharField(max_length=255, null=True, blank=True)
    segmento_v3 = models.CharField(max_length=255, null=True, blank=True)
    sla_tecnica = models.CharField(max_length=255, null=True, blank=True)
    status_rede = models.CharField(max_length=255, null=True, blank=True)
    eps_rede = models.CharField(max_length=255, null=True, blank=True)
    data_rede = models.DateField(null=True, blank=True)
    tipo_entrega = models.CharField(max_length=255, null=True, blank=True)
    data_sae = models.CharField(max_length=10, null=True, blank=True)
    agrupado = models.CharField(max_length=255, null=True, blank=True)
    pendencia_macro = models.CharField(max_length=255, null=True, blank=True)
    estimativa = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pedido} - {self.cliente}"

class ArquivoProcessado(models.Model):
    TIPO_CHOICES = [
        ('REPORT_B2B', 'Report B2B'),
        ('REDE_EXTERNA', 'Rede Externa'),
        ('REGRAS_NEGOCIO', 'Regras de Negócio'),
        ('EXPORTACAO', 'Exportação de Base'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PROCESSANDO', 'Processando'),
        ('CONCLUIDO', 'Concluído'),
        ('ERRO', 'Erro'),
    ]
    
    nome = models.CharField(max_length=255)
    tipo_arquivo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='REPORT_B2B')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_processamento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensagem = models.TextField(null=True, blank=True)
    registros_afetados = models.IntegerField(null=True, blank=True)
    tempo_processamento = models.FloatField(null=True, blank=True, help_text="Tempo de processamento em segundos")
    
    class Meta:
        ordering = ['-data_processamento']
    
    def __str__(self):
        return f"{self.nome} - {self.tipo_arquivo} - {self.status}"

class RegistroRevisao(models.Model):
    pedido = models.CharField(max_length=50, unique=True)
    status_anterior = models.CharField(max_length=255)
    status_atual = models.CharField(max_length=255)
    data_revisao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.pedido} - {self.status_anterior} -> {self.status_atual}"

class LogAlteracaoPendenciaMacro(models.Model):
    pedido = models.CharField(max_length=50)
    valor_anterior = models.CharField(max_length=255, null=True, blank=True)
    valor_novo = models.CharField(max_length=255, null=True, blank=True)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-data_alteracao']
    
    def __str__(self):
        return f"{self.pedido} - {self.valor_anterior} -> {self.valor_novo} por {self.usuario.username}"
