# RM4Health Dashboard Local

## 🚀 Execução Rápida

1. **Execute o arquivo**: `executar_dashboard.bat`
2. **Acesse no navegador**: http://localhost:8501
3. **Pronto!** O dashboard vai abrir automaticamente

## 📋 Funcionalidades

- ✅ **Dashboard interativo** com Streamlit
- ✅ **Gráficos dinâmicos** com Plotly
- ✅ **Carrega dados do REDCap** (com VPN)
- ✅ **Funciona offline** (com dados em cache)
- ✅ **Download de dados** em CSV
- ✅ **Análises automáticas** de qualquer dataset

## 🔧 Como Funciona

1. **Com VPN**: Conecta ao REDCap e baixa dados frescos
2. **Sem VPN**: Usa dados salvos localmente (arquivo `backup_redcap_data.csv`)

## 📊 Análises Incluídas

- **Visão Geral**: Gráficos de idade e gênero
- **Demografia**: Estatísticas detalhadas
- **Dados Raw**: Visualização completa dos dados
- **Estatísticas**: Métricas e completude

## ⚙️ Instalação Manual (se necessário)

```bash
pip install streamlit plotly pandas
streamlit run dashboard_local.py
```

## 📝 Notas

- **Porta padrão**: 8501
- **Auto-reload**: Atualiza automaticamente quando salva
- **Cache**: Dados ficam em cache por 5 minutos
