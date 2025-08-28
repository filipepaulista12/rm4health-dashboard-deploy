# Script PowerShell para deploy do RM4Health Dashboard no GitHub

Write-Host "🚀 Iniciando deploy do RM4Health Dashboard..." -ForegroundColor Green

# Verificar se estamos no diretório correto
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Erro: Execute este script no diretório do dashboard" -ForegroundColor Red
    exit 1
}

# Verificar se o Git está instalado
try {
    git --version | Out-Null
} catch {
    Write-Host "❌ Git não está instalado. Por favor, instale o Git primeiro." -ForegroundColor Red
    exit 1
}

# Configurar repositório se não existir
if (-not (Test-Path ".git")) {
    Write-Host "📁 Inicializando repositório Git..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
    git branch -M main
}

# Adicionar arquivos principais (excluindo arquivos de teste e debug)
Write-Host "📝 Adicionando arquivos essenciais ao Git..." -ForegroundColor Yellow

# Limpar arquivos desnecessários
$filesToRemove = @(
    "test_*.py",
    "debug_*.py", 
    "verify_*.py",
    "diagnostico.py",
    "investigate_*.py",
    "detailed_*.json",
    "field_analysis.json",
    "redcap_field_analysis.json"
)

foreach ($pattern in $filesToRemove) {
    Get-ChildItem $pattern -ErrorAction SilentlyContinue | Remove-Item -Force
    Write-Host "🗑️  Removido: $pattern" -ForegroundColor Gray
}

# Remover README antigo e renomear o novo
if (Test-Path "README.md") {
    Remove-Item "README.md" -Force
}
if (Test-Path "README_DEPLOY.md") {
    Rename-Item "README_DEPLOY.md" "README.md"
}

# Adicionar arquivos ao Git
git add .
git add .gitignore

Write-Host "💾 Fazendo commit das alterações..." -ForegroundColor Yellow
git commit -m "feat: Complete RM4Health Dashboard v2.0

✨ New Features:
- 🔍 Comprehensive Data Quality Analysis
- 💤 Enhanced Sleep Pattern Analysis  
- 💊 Advanced Medication Adherence Tracking
- 🏥 Healthcare Utilization Insights
- 👥 Detailed Caregiver Analysis
- 📊 Real-time REDCap Integration

🎨 UI/UX Improvements:
- Modern glassmorphism design
- Responsive Bootstrap 5 layout
- Interactive charts and visualizations
- Professional color schemes
- Enhanced navigation

🔧 Technical Enhancements:
- Optimized data processing pipeline
- Improved error handling
- Better caching mechanisms
- Enhanced API integration
- Comprehensive logging

📈 Analytics:
- Missing data pattern detection
- Temporal consistency checks
- Instrument quality assessment
- Automated recommendations
- Statistical correlations

This version represents a complete overhaul with professional-grade
analytics, modern UI, and robust data processing capabilities."

Write-Host "🔄 Enviando para o GitHub (force push para substituir versão antiga)..." -ForegroundColor Yellow
git push -f origin main

Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "🌐 Acesse: https://github.com/filipepaulista12/rm4health-dashboard-deploy" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Verifique se todos os arquivos foram enviados corretamente" -ForegroundColor White
Write-Host "2. Configure as variáveis de ambiente no servidor" -ForegroundColor White  
Write-Host "3. Teste a aplicação em produção" -ForegroundColor White
Write-Host "4. Configure o deployment automático se necessário" -ForegroundColor White
