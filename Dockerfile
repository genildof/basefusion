FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=basefusion.settings
ENV DEBUG=False
ENV SECRET_KEY=g=%jw)yyl1(_o16&ebdp=u4mc&!!e+s)3^!(s30szuwvrw#i$0
ENV ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
ENV DATABASE_URL=sqlite:///data/db.sqlite3

# Definir diretório de trabalho
WORKDIR /app

# Clonar o repositório
ARG REPO_URL=https://github.com/genildof/basefusion.git
ARG BRANCH=main
RUN git clone --depth 1 -b ${BRANCH} ${REPO_URL} .

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/data /app/media /app/static

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Executar collectstatic
RUN python manage.py collectstatic --noinput

# Criar arquivo .env com as configurações
RUN echo "DEBUG=False\n\
SECRET_KEY=${SECRET_KEY}\n\
ALLOWED_HOSTS=${ALLOWED_HOSTS}\n\
DATABASE_URL=${DATABASE_URL}\n\
REPO_URL=${REPO_URL}\n\
BRANCH=${BRANCH}" > /app/.env

# Criar diretório para volume de dados
VOLUME ["/app/data", "/app/media", "/app/static"]

# Expor a porta
EXPOSE 8000

# Criar arquivo de inicialização
RUN echo '#!/bin/bash\n\
# Verificar e criar o banco de dados se não existir\n\
mkdir -p /app/data\n\
touch /app/data/db.sqlite3\n\
# Executar migrações\n\
python manage.py migrate --noinput\n\
# Iniciar Gunicorn\n\
exec gunicorn basefusion.wsgi:application --bind 0.0.0.0:8000 --workers=2 --threads=4 --worker-tmp-dir=/dev/shm --timeout=120' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

# Comando para iniciar a aplicação
CMD ["/app/entrypoint.sh"] 