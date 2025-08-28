@echo off
echo 🚀 Iniciando deploy do RM4Health Dashboard...

cd /d "C:\Users\up739088\Desktop\FMUP\rm4isep\redcap-dashboard-simples"

echo 📁 Limpando arquivos desnecessários...
del /f /q test_*.py 2>nul
del /f /q debug_*.py 2>nul
del /f /q verify_*.py 2>nul
del /f /q diagnostico.py 2>nul
del /f /q investigate_*.py 2>nul
del /f /q detailed_*.json 2>nul
del /f /q field_analysis.json 2>nul
del /f /q redcap_field_analysis.json 2>nul

echo 📝 Configurando README...
if exist "README.md" del /f /q "README.md"
if exist "README_DEPLOY.md" ren "README_DEPLOY.md" "README.md"

echo 🔧 Configurando Git...
git config --global user.name "Filipe Paulista"
git config --global user.email "filipepaulista12@gmail.com"

echo 📦 Inicializando repositório...
git init
git remote remove origin 2>nul
git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
git branch -M main

echo 📋 Adicionando arquivos...
git add .

echo 💾 Fazendo commit...
git commit -m "feat: Complete RM4Health Dashboard v2.0 - Professional analytics dashboard with comprehensive data quality analysis, enhanced sleep/medication tracking, and modern UI"

echo 🚀 Enviando para GitHub...
git push -f origin main

echo ✅ Deploy concluído!
echo 🌐 Acesse: https://github.com/filipepaulista12/rm4health-dashboard-deploy

pause
