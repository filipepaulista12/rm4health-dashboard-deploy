# 🚀 Guia de Deploy - RM4Health Dashboard

## Instruções Passo a Passo para Deploy no GitHub

### 1️⃣ Preparação Inicial

Abra o PowerShell como Administrador e execute os seguintes comandos:

```powershell
# Navegar para o diretório do projeto
cd "C:\Users\up739088\Desktop\FMUP\rm4isep\redcap-dashboard-simples"

# Verificar se o Git está instalado
git --version
```

### 2️⃣ Configuração do Git (se necessário)

```powershell
# Configurar seu nome e email (substitua pelos seus dados)
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@gmail.com"
```

### 3️⃣ Limpeza de Arquivos Desnecessários

Execute estes comandos para remover arquivos que não precisam ir para produção:

```powershell
# Remover arquivos de teste e debug
Remove-Item "test_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "debug_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "verify_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "diagnostico.py" -Force -ErrorAction SilentlyContinue
Remove-Item "investigate_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "detailed_*.json" -Force -ErrorAction SilentlyContinue
Remove-Item "field_analysis.json" -Force -ErrorAction SilentlyContinue
Remove-Item "redcap_field_analysis.json" -Force -ErrorAction SilentlyContinue

# Remover README antigo e renomear o novo
Remove-Item "README.md" -Force -ErrorAction SilentlyContinue
Rename-Item "README_DEPLOY.md" "README.md" -ErrorAction SilentlyContinue
```

### 4️⃣ Inicialização do Repositório Git

```powershell
# Inicializar repositório (se ainda não foi feito)
git init

# Adicionar origem remota
git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git

# Definir branch principal
git branch -M main
```

### 5️⃣ Adicionar Arquivos ao Git

```powershell
# Adicionar todos os arquivos
git add .

# Verificar quais arquivos foram adicionados
git status
```

### 6️⃣ Fazer Commit

```powershell
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

This version represents a complete overhaul with professional-grade
analytics, modern UI, and robust data processing capabilities."
```

### 7️⃣ Push para GitHub (Force Push)

```powershell
# Force push para substituir completamente a versão antiga
git push -f origin main
```

### 8️⃣ Verificação

Após o push, verifique:
1. Acesse: https://github.com/filipepaulista12/rm4health-dashboard-deploy
2. Confirme que todos os arquivos foram enviados
3. Verifique se o README.md aparece corretamente
4. Teste se o repositório está funcionando

---

## 🔧 Resolução de Problemas

### Se der erro de autenticação:
```powershell
# Configurar credenciais
git config --global credential.helper manager-core
```

### Se der erro de branch:
```powershell
# Criar e mudar para branch main
git checkout -b main
git push -u origin main
```

### Se quiser ver o que vai ser enviado:
```powershell
git log --oneline
git diff --name-only
```

---

## 📁 Arquivos que serão enviados:

### ✅ Arquivos Principais:
- `app.py` - Aplicação Flask principal
- `config.py` - Configurações
- `data_processor.py` - Processamento de dados
- `redcap_client.py` - Cliente REDCap
- `requirements.txt` - Dependências
- `README.md` - Documentação
- `.gitignore` - Arquivos ignorados

### ✅ Templates HTML:
- `templates/dashboard.html`
- `templates/sleep_analysis.html`
- `templates/medication_adherence.html`
- `templates/healthcare_utilization.html`
- `templates/caregiver_analysis.html`
- `templates/data_quality.html`

### ✅ Arquivos Estáticos:
- `static/css/` - Estilos
- `static/js/` - JavaScript

### ❌ Arquivos que NÃO serão enviados:
- Arquivos de teste (`test_*.py`)
- Arquivos de debug (`debug_*.py`)
- Arquivos de investigação (`investigate_*.py`)
- Arquivos JSON temporários
- Cache (`__pycache__/`)

---

## 🎉 Após o Deploy

1. **Configure no servidor de produção:**
   - Instale as dependências: `pip install -r requirements.txt`
   - Configure as variáveis de ambiente
   - Configure o token REDCap

2. **Teste a aplicação:**
   - Execute: `python app.py`
   - Acesse: `http://localhost:5000`

3. **Deploy em produção (opcional):**
   - Heroku, Vercel, ou outro provedor
   - Configure as variáveis de ambiente
   - Configure o domínio personalizado

**🚀 Sua nova versão do dashboard está pronta para uso!**
