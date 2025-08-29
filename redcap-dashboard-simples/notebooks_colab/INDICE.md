#  RM4Health - Notebooks com Funções Reais

##  **Sistema RM4Health com Google Colab**

Esta versão contém **4 notebooks completos** com as **funções reais** do sistema RM4Health, utilizando **dados reais** do REDCap. Todos os notebooks são otimizados para execução no Google Colab.

##  **Notebooks Disponíveis**

### 1.  **`rm4health_analise_completa_real.ipynb`**
- **Descrição**: Análise completa com todas as funções principais do sistema
- **Funções Reais**: `RM4HealthProcessor`, `get_basic_stats()`, `calculate_adherence_rates_real()`, `detect_health_deterioration_real()`
- **Dados**: CSV real do REDCap com 514 colunas
- **Visualizações**: Estatísticas básicas, análise de aderência, detecção de deterioração

### 2.  **`rm4health_medicacao_real.ipynb`** 
- **Descrição**: Análise de medicação e aderência - replicação exata da função do dashboard
- **Funções Reais**: `calculate_adherence_rates()`, `analyze_adherence_factors()`
- **Algoritmo**: Escala de 4 pontos (Sim=4, Não=0, Às vezes=2)
- **Análises**: Aderência por participante, medicação específica, correlação com idade

### 3.  **`rm4health_sono_psqi_real.ipynb`**
- **Descrição**: Análise científica de qualidade do sono usando algoritmo PSQI
- **Algoritmo PSQI**: 7 componentes (0-3 pontos cada), thresholds científicos (5 bom, >10 intervenção)
- **Campos Reais**: hora_deitar, tempo_adormecer, qualidade_sono, etc.
- **Visualizações**: Radar charts, distribuições por componente, análise de risco

### 4.  **`rm4health_servicos_saude_real.ipynb`**
- **Descrição**: Análise de utilização de serviços de saúde e preditores
- **Funções Reais**: `identify_utilization_predictors_rm4health()`
- **Algoritmo**: Percentil 75 para identificação de alto utilizadores
- **Análises**: Consultas programadas, urgências, internamentos, preditores de utilização

##  **Dados**
- **Arquivo**: `../data/rm4health_dados_reais.csv`
- **Fonte**: REDCap export real (RM4HealthRemoteMonit_DATA_LABELS_2025-08-11_0937.csv)
- **Colunas**: 514 variáveis reais do projeto
- **Participantes**: Dados reais de pacientes (anonimizados)

##  **Como Usar**

### Google Colab (Recomendado)
1. Acesse: https://colab.research.google.com/
2. Clique em "GitHub" 
3. Cole o URL: `https://github.com/filipepaulista12/rm4health-dashboard-deploy`
4. Selecione o branch: `notebooks-google-colab`
5. Escolha um dos 4 notebooks
6. Execute célula por célula (Ctrl+Enter)

### Características dos Notebooks
-  **Auto-setup**: Clona repositório e instala dependências automaticamente
-  **Dados Reais**: Utiliza CSV real do REDCap (não dados mock)
-  **Funções Reais**: Replica exatamente as funções do sistema dashboard
-  **Algoritmos Científicos**: PSQI, scoring de aderência, detecção de risco
-  **Visualizações Profissionais**: Gráficos prontos para apresentações

##  **Requisitos**
- Conta Google (para Google Colab)
- Conexão à internet
- Navegador web moderno

##  **Nota Importante**
Todos os notebooks utilizam **funções reais** extraídas do sistema `data_processor.py` e **dados reais** do REDCap. Não são templates ou exemplos - são ferramentas funcionais para análise completa do projeto RM4Health.

---
*Notebooks criados com base nas funções reais do sistema RM4Health para uso pelos colaboradores do projeto.*
