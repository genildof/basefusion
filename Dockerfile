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

# Definir diretório de trabalho
WORKDIR /app

# Clonar o repositório (substitua a URL pelo seu repositório real)
# Se você quiser usar uma branch específica, adicione -b branch_name
ARG REPO_URL=https://github.com/genildof/basefusion.git
ARG BRANCH=main
RUN git clone --depth 1 -b ${BRANCH} ${REPO_URL} .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Criar diretórios necessários se não existirem
RUN mkdir -p /app/staticfiles /app/data /app/media /app/static

# Executar collectstatic
RUN python manage.py collectstatic --noinput

# Expor a porta
EXPOSE 8000

# Criar arquivo de inicialização
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
exec gunicorn basefusion.wsgi:application --bind 0.0.0.0:8000 --workers=2 --threads=4 --worker-tmp-dir=/dev/shm --timeout=120' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

# Comando para iniciar a aplicação
CMD ["/app/entrypoint.sh"] 