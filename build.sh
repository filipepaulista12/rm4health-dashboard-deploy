#!/bin/bash
# Build script for Render.com

echo "🔧 Iniciando build para produção..."

# Upgrade pip and core tools
echo "📦 Atualizando ferramentas base..."
pip install --upgrade pip setuptools wheel

# Install dependencies with no-deps for problematic packages
echo "📚 Instalando dependências..."
pip install --no-deps pandas==2.0.3
pip install numpy>=1.24.0
pip install -r requirements_production.txt

echo "✅ Build concluído!"
