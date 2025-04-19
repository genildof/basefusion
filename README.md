# Sistema de Processamento de Dados

Este sistema permite o processamento e análise de dados de planilhas Excel, com foco em dados de pedidos e status.

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- virtualenv (opcional, mas recomendado)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/genildof/basefusion.git
cd basefusion
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações do banco de dados:
```bash
python manage.py migrate
```

5. Crie um superusuário (opcional):
```bash
python manage.py createsuperuser
```

6. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## Funcionalidades

1. **Upload de Arquivos**
   - Upload de três planilhas Excel diferentes
   - Validação de formato e estrutura dos arquivos
   - Indicador visual de progresso

2. **Processamento de Dados**
   - Processamento automático após upload
   - Correlação entre as bases de dados
   - Sanitização e transformação dos dados

3. **Revisão de Status**
   - Interface para revisão de status
   - Confirmação de status por operadores
   - Histórico de revisões

4. **Arquivos Processados**
   - Listagem de todos os arquivos processados
   - Download dos arquivos processados
   - Histórico de processamentos

## Estrutura do Projeto

```
basefusion/
├── processamento/          # Aplicação principal
│   ├── migrations/        # Migrações do banco de dados
│   ├── templates/         # Templates HTML
│   ├── static/           # Arquivos estáticos
│   ├── models.py         # Modelos do banco de dados
│   ├── views.py          # Views da aplicação
│   └── urls.py           # URLs da aplicação
├── media/                # Arquivos de mídia
│   ├── temp/            # Arquivos temporários
│   └── arquivos_processados/  # Arquivos processados
├── static/              # Arquivos estáticos globais
├── basefusion/          # Configurações do projeto
└── manage.py           # Script de gerenciamento
```

## Uso

1. Acesse a aplicação através do navegador em `http://localhost:8000`
2. Faça login (se criou um superusuário)
3. Navegue pelo menu para acessar as diferentes funcionalidades
4. Siga as instruções na interface para cada operação

## Suporte

Para suporte ou dúvidas, entre em contato com o administrador do sistema. 