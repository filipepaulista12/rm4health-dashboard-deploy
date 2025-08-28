# 🚨 INSTRUÇÕES FINAIS - EXECUTE MANUALMENTE

Como os terminais estão com problemas, execute estes passos manualmente:

## 1️⃣ Abrir PowerShell como Administrador
- Clique no botão Iniciar
- Digite "PowerShell"
- Clique com botão direito em "Windows PowerShell"
- Selecione "Executar como administrador"

## 2️⃣ Navegar para a pasta do projeto
```powershell
Set-Location "C:\Users\up739088\Desktop\FMUP\rm4isep\redcap-dashboard-simples"
```

## 3️⃣ Executar o script de deploy
```powershell
.\deploy.bat
```

**OU** se preferir, execute estes comandos um por um:

### Limpeza de arquivos:
```powershell
Remove-Item "test_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "debug_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "verify_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "diagnostico.py" -Force -ErrorAction SilentlyContinue
Remove-Item "investigate_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "detailed_*.json" -Force -ErrorAction SilentlyContinue
Remove-Item "field_analysis.json" -Force -ErrorAction SilentlyContinue
Remove-Item "redcap_field_analysis.json" -Force -ErrorAction SilentlyContinue
```

### Configurar README:
```powershell
if (Test-Path "README.md") { Remove-Item "README.md" -Force }
if (Test-Path "README_DEPLOY.md") { Rename-Item "README_DEPLOY.md" "README.md" }
```

### Configurar Git:
```powershell
git config --global user.name "Filipe Paulista"
git config --global user.email "filipepaulista12@gmail.com"
git init
git remote remove origin
git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
git branch -M main
```

### Deploy:
```powershell
git add .
git commit -m "feat: Complete RM4Health Dashboard v2.0"
git push -f origin main
```

## 🎉 Resultado
Depois de executar, acesse:
**https://github.com/filipepaulista12/rm4health-dashboard-deploy**

---

## ⚡ Alternativa Rápida - COPIE E COLE TUDO:

```powershell
Set-Location "C:\Users\up739088\Desktop\FMUP\rm4isep\redcap-dashboard-simples"
Remove-Item "test_*.py","debug_*.py","verify_*.py","diagnostico.py","investigate_*.py","detailed_*.json","field_analysis.json","redcap_field_analysis.json" -Force -ErrorAction SilentlyContinue
if (Test-Path "README.md") { Remove-Item "README.md" -Force }
if (Test-Path "README_DEPLOY.md") { Rename-Item "README_DEPLOY.md" "README.md" }
git config --global user.name "Filipe Paulista"
git config --global user.email "filipepaulista12@gmail.com"
git init
git remote remove origin 2>$null
git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
git branch -M main
git add .
git commit -m "feat: Complete RM4Health Dashboard v2.0 - Professional analytics with data quality analysis, enhanced sleep/medication tracking, and modern UI"
git push -f origin main
Write-Host "✅ Deploy concluído! Acesse: https://github.com/filipepaulista12/rm4health-dashboard-deploy" -ForegroundColor Green
```

**Copie esse bloco inteiro e cole no PowerShell!** 🚀
