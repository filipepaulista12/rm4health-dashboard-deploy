# ⚡ Deploy Rápido - Comandos Resumidos

Copie e cole estes comandos no PowerShell (como Administrador):

```powershell
# 1. Navegar para o diretório
cd "C:\Users\up739088\Desktop\FMUP\rm4isep\redcap-dashboard-simples"

# 2. Limpar arquivos desnecessários
Remove-Item "test_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "debug_*.py" -Force -ErrorAction SilentlyContinue  
Remove-Item "verify_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "diagnostico.py" -Force -ErrorAction SilentlyContinue
Remove-Item "investigate_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "detailed_*.json" -Force -ErrorAction SilentlyContinue
Remove-Item "field_analysis.json" -Force -ErrorAction SilentlyContinue
Remove-Item "redcap_field_analysis.json" -Force -ErrorAction SilentlyContinue
Remove-Item "README.md" -Force -ErrorAction SilentlyContinue
Rename-Item "README_DEPLOY.md" "README.md" -ErrorAction SilentlyContinue

# 3. Configurar Git (substitua pelos seus dados)
git config --global user.name "Filipe Paulista"
git config --global user.email "filipepaulista12@gmail.com"

# 4. Inicializar repositório
git init
git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
git branch -M main

# 5. Adicionar e commit
git add .
git commit -m "feat: Complete RM4Health Dashboard v2.0 - Professional analytics dashboard with data quality analysis, enhanced sleep/medication tracking, and modern UI"

# 6. Push (substitui versão antiga completamente)
git push -f origin main
```

🎉 **Pronto! Seu dashboard está no GitHub!**

Acesse: https://github.com/filipepaulista12/rm4health-dashboard-deploy
