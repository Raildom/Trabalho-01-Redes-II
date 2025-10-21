#!/bin/bash

# Script de validação do projeto

echo "=== Validação do Projeto Redes II ==="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success_count=0
total_tests=0

# Função para testar
test_item() {
    local test_name="$1"
    local test_command="$2"
    local success_message="$3"
    local failure_message="$4"
    
    echo -n "Testando $test_name... "
    total_tests=$((total_tests + 1))
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}[SUCESSO]${NC} $success_message"
        success_count=$((success_count + 1))
        return 0
    else
        echo -e "${RED}[ERRO]${NC} $failure_message"
        return 1
    fi
}

# Função para testar arquivos
test_file() {
    local file_path="$1"
    local description="$2"
    
    test_item "$description" "[ -f '$file_path' ]" "Arquivo encontrado" "Arquivo não encontrado: $file_path"
}

# Função para testar diretórios
test_dir() {
    local dir_path="$1"
    local description="$2"
    
    test_item "$description" "[ -d '$dir_path' ]" "Diretório encontrado" "Diretório não encontrado: $dir_path"
}

echo "1. Verificando estrutura de arquivos..."

# Testa estrutura de diretórios
test_dir "src" "Diretório src"
test_dir "docker" "Diretório docker"
test_dir "testes" "Diretório testes"

# Testa arquivos principais
test_file "src/configuracao.py" "Configuração"
test_file "src/servidor_sequencial.py" "Servidor sequencial"
test_file "src/servidor_concorrente.py" "Servidor concorrente"
test_file "src/cliente.py" "Cliente HTTP"
test_file "docker/Dockerfile.sequencial" "Dockerfile Sequencial"
test_file "docker/Dockerfile.concorrente" "Dockerfile Concorrente"
test_file "docker/Dockerfile.cliente" "Dockerfile Cliente"
test_file "docker/docker-compose.yml" "Docker Compose"
test_file "testes/teste_completo.py" "Testes completos"
test_file "testes/analisar_resultados.py" "Análise de resultados"
test_file "run_project.sh" "Script principal"
test_file "requisitos.txt" "Requirements"

echo ""
echo "2. Verificando pré-requisitos..."

# Testa Docker
test_item "Docker" "command -v docker" "Docker instalado" "Docker não encontrado"
test_item "Docker Compose" "command -v docker-compose" "Docker Compose instalado" "Docker Compose não encontrado"
test_item "Docker daemon" "docker info" "Docker rodando" "Docker não está rodando"

echo ""
echo "3. Verificando permissões..."

test_item "Script executável" "[ -x run_project.sh ]" "Script executável" "Script não é executável"

echo ""
echo "4. Validando configurações..."

# Verifica se a configuração está correta
test_item "Configuração Python" "python3 -c 'import sys; sys.path.append(\"src\"); from configuracao import *; print(MATRICULA)'" \
    "Configuração carregada" "Erro na configuração"

echo ""
echo "5. Testando sintaxe dos scripts Python..."

for script in src/*.py testes/*.py; do
    if [ -f "$script" ]; then
        script_name=$(basename "$script")
        test_item "Sintaxe $script_name" "python3 -m py_compile '$script'" \
            "Sintaxe válida" "Erro de sintaxe"
    fi
done

echo ""
echo "6. Verificando Docker Compose..."

test_item "Docker Compose válido" "cd docker && docker-compose config" \
    "Configuração válida" "Erro na configuração do Docker Compose"

echo ""
echo "=== Resumo da Validação ==="
echo -e "Testes passaram: ${GREEN}$success_count${NC}/$total_tests"

if [ $success_count -eq $total_tests ]; then
    echo -e "${GREEN}[SUCESSO] Projeto validado com sucesso!${NC}"
    echo ""
    echo "Proximos passos:"
    echo "1. Execute: ./run_project.sh start"
    echo "2. Execute: ./run_project.sh test"
    echo "3. Execute: ./run_project.sh full-test (opcional)"
    echo ""
    echo "Ou simplesmente: ./run_project.sh all"
    exit 0
else
    failed_tests=$((total_tests - success_count))
    echo -e "${RED}[ERRO] $failed_tests teste(s) falharam${NC}"
    echo ""
    echo "Corrija os problemas encontrados antes de executar o projeto."
    exit 1
fi
