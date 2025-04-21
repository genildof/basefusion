#!/usr/bin/env python3
import os
import sys
import time

# Adicionar o diretório do projeto ao path
sys.path.append('/home/sysadmin/Desktop/basefusion')

# Configurar variáveis de ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basefusion.settings')

try:
    # Importar Django e configurar
    import django
    django.setup()
    
    # Importar settings
    from django.conf import settings
    from django.db import connections
    
    # Obter configurações do banco de dados
    db_config = settings.DATABASES['default']
    
    print("Configuração do banco de dados:")
    print(f"ENGINE: {db_config['ENGINE']}")
    print(f"NAME: {db_config['NAME']}")
    
    if 'HOST' in db_config:
        print(f"HOST: {db_config['HOST']}")
    if 'USER' in db_config:
        print(f"USER: {db_config['USER']}")
    if 'PORT' in db_config:
        print(f"PORT: {db_config['PORT']}")
    
    # Verificar se está usando SQLite ou PostgreSQL
    if 'sqlite3' in db_config['ENGINE']:
        print("\nA aplicação está configurada para usar SQLite!")
        sqlite_path = db_config['NAME']
        if os.path.exists(sqlite_path):
            file_size = os.path.getsize(sqlite_path) / (1024 * 1024)  # Tamanho em MB
            print(f"Arquivo do banco SQLite: {sqlite_path}")
            print(f"Tamanho do arquivo SQLite: {file_size:.2f} MB")
            print(f"Última modificação: {time.ctime(os.path.getmtime(sqlite_path))}")
            
            # Tentar conectar ao SQLite
            try:
                conn = connections['default']
                conn.cursor()
                print("✅ Conexão com SQLite bem-sucedida!")
            except Exception as e:
                print(f"❌ Erro ao conectar ao SQLite: {str(e)}")
        else:
            print(f"Arquivo SQLite não encontrado: {sqlite_path}")
    else:
        print("\nA aplicação está configurada para usar PostgreSQL!")
        
        # Verificar se o arquivo SQLite existe no diretório do projeto
        sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")
        if os.path.exists(sqlite_path):
            file_size = os.path.getsize(sqlite_path) / (1024 * 1024)  # Tamanho em MB
            print(f"ATENÇÃO: Um arquivo SQLite foi encontrado no diretório do projeto!")
            print(f"Arquivo: {sqlite_path}")
            print(f"Tamanho: {file_size:.2f} MB")
            print(f"Última modificação: {time.ctime(os.path.getmtime(sqlite_path))}")
            print("A aplicação está configurada para PostgreSQL, mas pode estar usando SQLite!")
            
        # Tentar conectar ao PostgreSQL
        try:
            conn = connections['default']
            conn.cursor()
            print("✅ Conexão com PostgreSQL bem-sucedida!")
            
            # Verificar se há dados na tabela auth_user
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
            print(f"Número de usuários no banco PostgreSQL: {user_count}")
            
            # Verificar se há dados em alguma tabela da aplicação
            try:
                cursor.execute("SELECT count(*) FROM processamento_baseconsolidada")
                record_count = cursor.fetchone()[0]
                print(f"Número de registros em BaseConsolidada: {record_count}")
            except:
                print("Tabela BaseConsolidada não encontrada ou vazia")
                
        except Exception as e:
            print(f"❌ Erro ao conectar ao PostgreSQL: {str(e)}")
            print("A aplicação não consegue conectar ao PostgreSQL!")
            
            # Verifique se o Docker está em execução
            print("\nVerificando o estado dos containers Docker:")
            os.system("docker ps | grep fieldmanager_postgresql || echo 'Container PostgreSQL não está rodando'")
            
except Exception as e:
    print(f"Erro ao verificar configuração do banco de dados: {str(e)}") 