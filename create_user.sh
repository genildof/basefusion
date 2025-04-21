#!/bin/bash

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
  echo "Erro: Docker não está em execução. Inicie o Docker e tente novamente."
  exit 1
fi

# Executar o script de criação de usuário dentro do container
echo "Executando script para criar usuário padrão..."
docker exec -it basefusion python3 /app/create_default_user.py
echo "Concluído!" 