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

def verificar_usuario():
    try:
        # Verificar se o usuário existe
        if User.objects.filter(username="sysadmin").exists():
            usuario = User.objects.get(username="sysadmin")
            print(f"Usuário 'sysadmin' encontrado (ID: {usuario.id})")
            print(f"Superusuário: {usuario.is_superuser}")
            print(f"Staff: {usuario.is_staff}")
            print(f"Ativo: {usuario.is_active}")
            
            # Verificar perfil
            try:
                perfil = PerfilUsuario.objects.get(usuario=usuario)
                print(f"Perfil encontrado (ID: {perfil.id})")
                print(f"Tipo de perfil: {perfil.perfil}")
                print(f"Perfil é SUPERVISOR: {perfil.perfil == 'SUPERVISOR'}")
                print(f"Perfil é OPERADOR: {perfil.perfil == 'OPERADOR'}")
                
                # Corrigir o perfil se necessário
                if perfil.perfil != 'SUPERVISOR':
                    perfil.perfil = 'SUPERVISOR'
                    perfil.save()
                    print("Perfil atualizado para SUPERVISOR!")
            except PerfilUsuario.DoesNotExist:
                print("Perfil não encontrado. Criando perfil SUPERVISOR...")
                PerfilUsuario.objects.create(
                    usuario=usuario,
                    perfil="SUPERVISOR"
                )
                print("Perfil SUPERVISOR criado com sucesso!")
        else:
            print("Usuário 'sysadmin' não encontrado!")
            
        # Listar todos os usuários e seus perfis
        print("\nLista de todos os usuários:")
        for user in User.objects.all():
            try:
                perfil = PerfilUsuario.objects.get(usuario=user)
                tipo_perfil = perfil.perfil
            except PerfilUsuario.DoesNotExist:
                tipo_perfil = "Sem perfil"
                
            print(f"- {user.username}: {tipo_perfil}")
    except Exception as e:
        print(f"Erro ao verificar usuário: {e}")

if __name__ == "__main__":
    print("Verificando usuário 'sysadmin'...")
    verificar_usuario()
    print("Verificação concluída.") 