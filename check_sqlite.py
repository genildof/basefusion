#!/usr/bin/env python3
import os
import sqlite3
import time

# Caminho para o arquivo SQLite
sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")

try:
    # Verificar se o arquivo existe
    if not os.path.exists(sqlite_path):
        print(f"Arquivo SQLite não encontrado: {sqlite_path}")
        exit(1)
    
    # Obter informações sobre o arquivo
    file_size = os.path.getsize(sqlite_path) / (1024 * 1024)  # Tamanho em MB
    print(f"Arquivo SQLite: {sqlite_path}")
    print(f"Tamanho: {file_size:.2f} MB")
    print(f"Última modificação: {time.ctime(os.path.getmtime(sqlite_path))}")
    
    # Conectar ao banco de dados SQLite
    print("\nTentando conectar ao banco de dados SQLite...")
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    print("✅ Conexão com SQLite bem-sucedida!")
    
    # Listar tabelas
    print("\nTabelas no banco de dados:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"- {table_name}")
    
    # Verificar dados nas tabelas importantes
    print("\nVerificação de dados nas tabelas principais:")
    
    # Verificar usuários
    try:
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        user_count = cursor.fetchone()[0]
        print(f"Usuários (auth_user): {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, username, is_superuser, is_staff, is_active FROM auth_user LIMIT 5;")
            users = cursor.fetchall()
            print("\nPrimeiros 5 usuários:")
            for user in users:
                print(f"  ID: {user[0]}, Username: {user[1]}, SuperUser: {user[2]}, Staff: {user[3]}, Active: {user[4]}")
    except sqlite3.OperationalError as e:
        print(f"Erro ao consultar usuários: {str(e)}")
    
    # Verificar BaseConsolidada
    try:
        cursor.execute("SELECT COUNT(*) FROM processamento_baseconsolidada;")
        record_count = cursor.fetchone()[0]
        print(f"BaseConsolidada: {record_count} registros")
    except sqlite3.OperationalError as e:
        print(f"Erro ao consultar BaseConsolidada: {str(e)}")
    
    # Verificar PerfilUsuario
    try:
        cursor.execute("SELECT COUNT(*) FROM processamento_perfilusuario;")
        perfil_count = cursor.fetchone()[0]
        print(f"PerfilUsuario: {perfil_count} registros")
        
        if perfil_count > 0:
            cursor.execute("SELECT id, usuario_id, perfil FROM processamento_perfilusuario LIMIT 5;")
            perfis = cursor.fetchall()
            print("\nPrimeiros 5 perfis:")
            for perfil in perfis:
                print(f"  ID: {perfil[0]}, Usuario_ID: {perfil[1]}, Perfil: {perfil[2]}")
    except sqlite3.OperationalError as e:
        print(f"Erro ao consultar PerfilUsuario: {str(e)}")
        
    # Fechar conexão
    conn.close()
    
except Exception as e:
    print(f"Erro ao analisar o banco SQLite: {str(e)}") 