FROM python:3.10-slim

# Instalar dependências do sistema e configurar locale
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    locales \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8

# Configurar variáveis de ambiente para locale
ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=basefusion.settings

# Definir argumentos de build
ARG DATABASE_URL
ENV DATABASE_URL=${DATABASE_URL}

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements.txt primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos do projeto
COPY . /app/

# Criar diretórios necessários se não existirem
RUN mkdir -p /app/staticfiles /app/data /app/media /app/static

# Manter script para criação de usuário padrão (para execução manual)
COPY create_default_user.py /app/create_default_user.py
RUN chmod +x /app/create_default_user.py

# Executar collectstatic
RUN python3 manage.py collectstatic --noinput

# Expor a porta
EXPOSE 8000

# Criar arquivo de inicialização com criação automática do usuário sysadmin
RUN echo '#!/bin/bash\n\
# Aguardar o banco de dados estar disponível\n\
echo "Aguardando conexão com o PostgreSQL..."\n\
while ! pg_isready -h fieldmanager_postgresql -U postgres -q; do\n\
  sleep 1\n\
done\n\
\n\
echo "PostgreSQL conectado, executando migrações..."\n\
python3 manage.py migrate --noinput\n\
\n\
echo "Criando usuário padrão sysadmin com perfil SUPERVISOR..."\n\
python3 create_default_user.py\n\
\n\
echo "Iniciando servidor..."\n\
exec gunicorn basefusion.wsgi:application --bind 0.0.0.0:8000 --workers=2 --threads=4 --worker-tmp-dir=/dev/shm --timeout=120 --max-requests 1000 --max-requests-jitter 50\n\
' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

# Comando para iniciar a aplicação
CMD ["/app/entrypoint.sh"] 