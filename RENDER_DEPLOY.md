# Render.com Deploy Configuration

## ⚙️ Configurações do Render

### **Tipo de Serviço**: Web Service

### **Configurações Básicas**:
- **Repository**: `filipepaulista12/rm4health-dashboard-deploy`
- **Branch**: `deploy-online-compartilhado`
- **Runtime**: `Python 3.11`

### **Build & Deploy**:
```bash
# Build Command (CORRIGIDO):
pip install --upgrade pip setuptools wheel && pip install -r requirements_production.txt

# Start Command:
python production_server.py
```

### **Variáveis de Ambiente**:
- `PORT`: (Render define automaticamente)
- `HOST`: `0.0.0.0`

### **Configurações Avançadas**:
- **Health Check Path**: `/`
- **Auto-Deploy**: `Yes` (deploy automático em push)

## 📋 Checklist de Deploy:

- [✅] Código no GitHub (branch: deploy-online-compartilhado)
- [✅] requirements_production.txt criado
- [✅] production_server.py configurado
- [✅] Dados locais incluídos
- [✅] Procfile criado
- [⏳] Deploy no Render.com

## 🌐 Após Deploy:

- URL será: `https://[seu-app-name].onrender.com`
- Dashboard funcionará sem VPN
- Dados estáticos (596 registros)
- Todas análises funcionando
