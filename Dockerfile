FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=basefusion.settings

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements.txt primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos do projeto
COPY . /app/

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