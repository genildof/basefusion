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
RUN echo 'from django.contrib.auth.models import User\n\
from processamento.models import PerfilUsuario\n\
from django.db import IntegrityError\n\
\n\
def create_default_user():\n\
    try:\n\
        # Verifica se o usuário já existe\n\
        if not User.objects.filter(username="sysadmin").exists():\n\
            # Cria o usuário sysadmin\n\
            user = User.objects.create_superuser(\n\
                username="sysadmin",\n\
                email="sysadmin@example.com",\n\
                password="@Password22"\n\
            )\n\
            print("Usuário sysadmin criado com sucesso!")\n\
        else:\n\
            user = User.objects.get(username="sysadmin")\n\
            # Garante que o usuário tem permissões de superuser\n\
            if not user.is_superuser:\n\
                user.is_superuser = True\n\
                user.is_staff = True\n\
                user.save()\n\
                print("Usuário sysadmin atualizado para superuser!")\n\
        \n\
        # Verifica se o usuário já tem perfil\n\
        try:\n\
            perfil = PerfilUsuario.objects.get(user__username="sysadmin")\n\
            # Atualiza o perfil para SUPERVISOR se necessário\n\
            if perfil.perfil != "SUPERVISOR" or not perfil.is_supervisor:\n\
                perfil.perfil = "SUPERVISOR"\n\
                perfil.is_supervisor = True\n\
                perfil.save()\n\
                print("Perfil do usuário sysadmin atualizado para SUPERVISOR!")\n\
        except PerfilUsuario.DoesNotExist:\n\
            # Cria perfil SUPERVISOR para o usuário\n\
            user = User.objects.get(username="sysadmin")\n\
            perfil = PerfilUsuario.objects.create(\n\
                user=user,\n\
                perfil="SUPERVISOR",\n\
                is_supervisor=True\n\
            )\n\
            print("Perfil SUPERVISOR criado para o usuário sysadmin!")\n\
    except IntegrityError as e:\n\
        print(f"Erro ao criar usuário padrão: {e}")\n\
    except Exception as e:\n\
        print(f"Erro inesperado: {e}")\n\
\n\
# Importamos aqui para garantir que o Django esteja configurado\n\
if __name__ == "__main__":\n\
    import django\n\
    django.setup()\n\
    create_default_user()\n\
' > /app/create_default_user.py

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
python create_default_user.py\n\
\n\
echo "Iniciando servidor..."\n\
exec gunicorn basefusion.wsgi:application --bind 0.0.0.0:8000 --workers=2 --threads=4 --worker-tmp-dir=/dev/shm --timeout=120 --max-requests 1000 --max-requests-jitter 50\n\
' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

# Comando para iniciar a aplicação
CMD ["/app/entrypoint.sh"] 