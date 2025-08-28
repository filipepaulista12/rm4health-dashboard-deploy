#!/bin/bash
# Script para deploy do RM4Health Dashboard no GitHub

echo "🚀 Iniciando deploy do RM4Health Dashboard..."

# Verificar se estamos no diretório correto
if [ ! -f "app.py" ]; then
    echo "❌ Erro: Execute este script no diretório do dashboard"
    exit 1
fi

# Verificar se o Git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não está instalado. Por favor, instale o Git primeiro."
    exit 1
fi

# Configurar repositório se não existir
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositório Git..."
    git init
    git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
fi

# Verificar se há alterações
if git diff --quiet && git diff --staged --quiet; then
    echo "ℹ️  Não há alterações para commit"
else
    echo "📝 Adicionando arquivos ao Git..."
    git add .
    
    echo "💾 Fazendo commit das alterações..."
    git commit -m "feat: Update RM4Health Dashboard with new features

- Added comprehensive data quality analysis
- Enhanced sleep analysis with detailed metrics
- Improved medication adherence tracking
- Added healthcare utilization insights
- Enhanced caregiver analysis
- Updated UI with modern design
- Added real-time data processing
- Improved error handling and validation"
fi

echo "🔄 Enviando para o GitHub..."
git push -f origin main

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Acesse: https://github.com/filipepaulista12/rm4health-dashboard-deploy"
