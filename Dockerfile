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

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements.txt primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos do projeto
COPY . /app/

# Criar diretórios necessários se não existirem
RUN mkdir -p /app/staticfiles /app/data /app/media /app/static

# Criar script para inicialização e criação de usuário padrão
COPY create_default_user.py /app/create_default_user.py
RUN chmod +x /app/create_default_user.py

# Executar collectstatic
RUN python manage.py collectstatic --noinput

# Expor a porta
EXPOSE 8000

# Criar arquivo de inicialização
RUN echo '#!/bin/bash\n\
# Aguardar o banco de dados estar disponível\n\
echo "Aguardando conexão com o PostgreSQL..."\n\
while ! pg_isready -h fieldmanager_postgresql -U postgres -q; do\n\
  sleep 1\n\
done\n\
\n\
echo "PostgreSQL conectado, executando migrações..."\n\
python manage.py migrate --noinput\n\
\n\
echo "Criando usuário padrão..."\n\
python manage.py shell -c "from django.contrib.auth.models import User; from processamento.models import PerfilUsuario; u, created = User.objects.get_or_create(username=\"sysadmin\", defaults={\"is_superuser\": True, \"is_staff\": True, \"email\": \"sysadmin@example.com\"}); u.set_password(\"@Password22\"); u.save(); try: perfil = PerfilUsuario.objects.get(usuario=u); perfil.perfil = \"SUPERVISOR\"; perfil.save(); print(\"Perfil atualizado para SUPERVISOR\"); except PerfilUsuario.DoesNotExist: PerfilUsuario.objects.create(usuario=u, perfil=\"SUPERVISOR\"); print(\"Perfil SUPERVISOR criado para usuário sysadmin\");" \n\
\n\
echo "Iniciando servidor..."\n\
exec gunicorn basefusion.wsgi:application --bind 0.0.0.0:8000 --workers=2 --threads=4 --worker-tmp-dir=/dev/shm --timeout=120 --max-requests 1000 --max-requests-jitter 50\n\
' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

# Comando para iniciar a aplicação
CMD ["/app/entrypoint.sh"] 