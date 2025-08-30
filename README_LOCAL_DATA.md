# RM4Health Dashboard - Versão com Dados Locais

## 📋 Overview

Esta versão do dashboard funciona **sem conexão com a API do REDCap**, usando dados estáticos extraídos previamente. Mantém todas as funcionalidades de análise intactas.

## 🎯 Funcionalidades

### ✅ Implementado
- **Extração de dados** da API para arquivos locais
- **Cliente local** que simula a API original
- **Compatibilidade total** com análises existentes
- **Dados em múltiplos formatos** (JSON, CSV)
- **Cache otimizado** para performance

### 🔄 Estrutura de Dados

```
📂 Arquivos Gerados:
├── redcap_data_YYYYMMDD_HHMMSS.json     # Dados completos
├── redcap_raw_YYYYMMDD_HHMMSS.csv       # Dados RAW
├── redcap_labeled_YYYYMMDD_HHMMSS.csv   # Dados LABELED
├── redcap_metadata_YYYYMMDD_HHMMSS.csv  # Metadados
└── local_data_config.json               # Configuração
```

## 🚀 Como Usar

### 1. Extrair Dados (apenas uma vez)
```bash
python extract_data.py
```

### 2. Executar Dashboard Local
```bash
python app.py
```

### 3. Acessar
- **Local**: http://127.0.0.1:5000
- **Rede**: http://[SEU_IP]:5000

## ⚙️ Configuração

No arquivo `config.py`:

```python
# Para usar dados locais
USE_LOCAL_DATA = True

# Para usar API (requer VPN)
USE_LOCAL_DATA = False
```

## 📊 Dados Atuais

- **Registros**: 596 participantes
- **Campos**: 254 variáveis
- **Extração**: 30/08/2025 10:49:39

## 🔧 Vantagens

1. **Sem VPN**: Funciona sem conexão com REDCap
2. **Performance**: Dados em cache local
3. **Offline**: Não depende de internet
4. **Portabilidade**: Pode ser movido para qualquer servidor
5. **Análises Intactas**: Zero modificações nas análises

## 📝 Próximos Passos

1. **Deploy online**: Hospedar em servidor web
2. **Atualizações**: Sistema para atualizar dados
3. **Backup**: Estratégia de backup dos dados
4. **Otimização**: Compressão e performance

## 🛠️ Arquivos Principais

- `extract_data.py` - Script de extração
- `local_redcap_client.py` - Cliente local
- `app.py` - Aplicação principal (modificada)
- `config.py` - Configurações (modificado)
