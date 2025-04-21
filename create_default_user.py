#!/usr/bin/env python
import os
import sys
import django

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basefusion.settings')
django.setup()

# Importar modelos após configurar o Django
from django.contrib.auth.models import User
from processamento.models import PerfilUsuario
from django.db import IntegrityError

def create_default_user():
    try:
        # Verifica se o usuário já existe
        if not User.objects.filter(username="sysadmin").exists():
            # Cria o usuário sysadmin
            user = User.objects.create_superuser(
                username="sysadmin",
                email="sysadmin@example.com",
                password="@Password22"
            )
            print("Usuário sysadmin criado com sucesso!")
        else:
            user = User.objects.get(username="sysadmin")
            # Garante que o usuário tem permissões de superuser
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                print("Usuário sysadmin atualizado para superuser!")

            # Garante que a senha está correta
            user.set_password("@Password22")
            user.save()
            print("Senha do usuário sysadmin atualizada!")
        
        # Verifica se o usuário já tem perfil
        try:
            perfil = PerfilUsuario.objects.get(usuario=user)
            # Atualiza o perfil para SUPERVISOR se necessário
            if perfil.perfil != "SUPERVISOR":
                perfil.perfil = "SUPERVISOR"
                perfil.save()
                print("Perfil do usuário sysadmin atualizado para SUPERVISOR!")
        except PerfilUsuario.DoesNotExist:
            # Cria perfil SUPERVISOR para o usuário
            perfil = PerfilUsuario.objects.create(
                usuario=user,
                perfil="SUPERVISOR"
            )
            print("Perfil SUPERVISOR criado para o usuário sysadmin!")
    except IntegrityError as e:
        print(f"Erro ao criar usuário padrão: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    print("Criando usuário padrão sysadmin...")
    create_default_user()
    print("Processo concluído.") 