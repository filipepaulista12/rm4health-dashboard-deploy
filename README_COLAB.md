# 📊 RM4Health Dashboard - Colab Integration

Sistema completo de análise de dados do projeto RM4Health com integração Google Colab e GitHub para colaboração em equipe.

## 🚀 Como Usar

### 1. Preparação dos Dados

1. **Faça upload do seu arquivo CSV** para a pasta `data/` do repositório
2. **Nomeie o arquivo** como `rm4health_dados.csv`
3. **Certifique-se** de que o arquivo está no formato correto (UTF-8, colunas adequadas)

### 2. Usando no Google Colab

1. **Abra qualquer notebook** da pasta `notebooks_colab/`
2. **Clique no botão "Open in Colab"** no topo do notebook
3. **Execute a primeira célula** - o sistema irá:
   - Detectar automaticamente o ambiente Colab
   - Clonar o repositório GitHub
   - Carregar os dados CSV
   - Configurar o ambiente de análise

### 3. Usando em Ambiente Local

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
   cd rm4health-dashboard-deploy
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute os notebooks** normalmente no Jupyter/VS Code

## 📁 Estrutura do Projeto

```
rm4health-dashboard-deploy/
├── data/
│   ├── rm4health_dados.csv          # Seus dados reais
│   └── rm4health_dados_exemplo.csv   # Dados de exemplo
├── notebooks_colab/
│   ├── rm4health_analise_geral.ipynb
│   ├── rm4health_qualidade_dados.ipynb
│   ├── rm4health_outcomes_clinicos.ipynb
│   └── ... (mais 14 notebooks)
├── results/
│   └── ... (resultados das análises)
└── README.md
```

## 📊 Notebooks Disponíveis

### Análises Principais
- **📈 Análise Geral** - Visão geral e exploratória dos dados
- **🔍 Qualidade dos Dados** - Análise de missing values e limpeza
- **🏥 Outcomes Clínicos** - Resultados de saúde e marcadores
- **💊 Análise de Medicação** - Padrões de uso e aderência
- **😴 Análise do Sono** - Qualidade e duração do sono
- **🔬 Comorbidades** - Doenças associadas e interações

### Análises Avançadas
- **🚑 Hospitalizações** - Padrões de internação
- **🚨 Urgências** - Visitas de emergência
- **⚠️ Alertas** - Sistema de alertas e notificações
- **📊 Análise de Riscos** - Fatores de risco e predição
- **👨‍👩‍👧‍👦 Cuidadores** - Análise do suporte familiar
- **🏥 Utilização de Serviços** - Acesso aos cuidados de saúde

### Análises Especiais
- **📱 Monitorização Remota** - Dispositivos e telemedicina
- **📅 Análise Longitudinal** - Tendências ao longo do tempo
- **💰 Custos** - Análise econômico dos cuidados
- **🔮 Predição** - Modelos preditivos de ML

## 🔧 Configuração Técnica

### Formato dos Dados CSV

O arquivo `rm4health_dados.csv` deve conter as seguintes colunas principais:

```csv
participant_id,participant_code,participant_group,sex,birth_year,
education_level,chronic_diseases,medications_current,blood_pressure_systolic,
blood_pressure_diastolic,bmi,glucose_level,hba1c,outcome_primary,
intervention_start_date,followup_1_date,costs_total,satisfaction_overall
```

### Dependências

```
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0
scipy>=1.7.0
scikit-learn>=1.0.0
```

## 🌐 Colab vs Local

| Recurso | Google Colab | Ambiente Local |
|---------|-------------|----------------|
| **Setup** | Automático | Manual |
| **GitHub** | Clone automático | Clone manual |
| **Dados** | Via repositório | Arquivo local |
| **Performance** | Limitada | Completa |
| **Persistência** | Sessão | Disco local |

## 📈 Próximos Passos

1. **Upload dos dados reais** para `data/rm4health_dados.csv`
2. **Teste dos notebooks** no Google Colab
3. **Personalização** das análises conforme necessidades
4. **Compartilhamento** com a equipe via GitHub
5. **Geração de relatórios** automáticos

## 🆘 Suporte

- **Documentação**: Verifique os comentários nos notebooks
- **Dados de exemplo**: Use `rm4health_dados_exemplo.csv` para testes
- **Erros comuns**: Verifique encoding UTF-8 e formato das datas

---

**🎯 Sistema pronto para análise colaborativa de dados RM4Health!**
