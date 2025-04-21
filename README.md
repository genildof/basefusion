# BaseFusion

Sistema de gerenciamento e processamento de dados para acompanhamento de pedidos.

## Requisitos

- Docker
- Docker Compose

## Configuração e Execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/basefusion.git
   cd basefusion
   ```

2. Execute o projeto com Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Acesse o sistema em:
   ```
   http://localhost:8000
   ```

## Persistência de Dados

O sistema está configurado para manter os dados persistentes entre deployments. Os volumes Docker seguintes são usados:

- `basefusion_postgres_data`: Armazena os dados do banco PostgreSQL
- `basefusion_app_data`: Armazena os dados da aplicação 
- `./media`: Armazena os arquivos de mídia
- `./static`: Armazena os arquivos estáticos

Estes volumes garantem que os dados não sejam perdidos quando os containers são recriados.

## Criação do Usuário Padrão

O sistema não cria automaticamente o usuário padrão durante o deploy para evitar a reconfiguração de usuários existentes. Para criar o usuário padrão manualmente, siga os passos abaixo:

1. Certifique-se de que os containers estejam em execução:
   ```bash
   docker ps
   ```

2. Execute o script de criação de usuário:
   ```bash
   ./create_user.sh
   ```

Isso criará um usuário com as seguintes credenciais:
- **Usuário**: sysadmin
- **Senha**: @Password22
- **Perfil**: SUPERVISOR

## Recriando a aplicação sem perder dados

Para atualizar a aplicação sem perder dados:

```bash
# Parar os containers
docker-compose down

# Reconstruir a imagem
docker-compose build

# Iniciar os containers novamente
docker-compose up -d
```

Os dados persistirão graças aos volumes configurados.

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