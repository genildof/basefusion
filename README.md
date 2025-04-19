# Base Fusion

Sistema de processamento e consolidação de dados para análise e gestão de pedidos.

## Funcionalidades Principais

- Importação de bases de dados externas
- Processamento de relatórios B2B
- Classificação automática de pedidos
- Sistema de revisão e aprovação
- Exportação de dados consolidados
- Regras de negócio automatizadas

## Tecnologias Utilizadas

- Python 3.9
- Django 5.2
- Pandas
- OpenPyXL
- Bootstrap 5
- SQLite

## Requisitos para Deploy

- Docker
- Docker Compose
- Easy Panel

## Instruções de Deploy

### 1. Configuração do Ambiente

```bash
# Clonar o repositório
git clone https://github.com/genildof/basefusion.git
cd basefusion

# Criar arquivo .env
cp .env.example .env
# Editar .env com suas configurações
```

### 2. Deploy com Docker

```bash
# Construir e iniciar os containers
docker-compose up -d

# Executar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser
```

### 3. Estrutura de Diretórios

```
basefusion/
├── data/           # Banco de dados SQLite
├── media/          # Arquivos de mídia
├── processamento/  # Código da aplicação
│   ├── modules/    # Módulos de processamento
│   ├── templates/  # Templates HTML
│   └── views.py    # Views da aplicação
├── Dockerfile      # Configuração do container
├── docker-compose.yml
└── requirements.txt
```

## Configurações Importantes

- O banco de dados SQLite é persistido em `data/db.sqlite3`
- Arquivos de mídia são armazenados em `media/`
- Configurações de ambiente no arquivo `.env`

## Monitoramento e Manutenção

### Logs
```bash
docker-compose logs -f
```

### Backup
```bash
# Backup do banco de dados
cp data/db.sqlite3 backup/db.sqlite3_$(date +%Y%m%d)
```

### Reinicialização
```bash
docker-compose restart
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença Apache 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes. 