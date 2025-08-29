# 📊 RM4Health - Notebooks Google Colab

Este diretório contém notebooks Jupyter especializados para análise dos dados do projeto RM4Health. Os notebooks foram desenvolvidos para serem executados no Google Colab, permitindo análise online dos dados sem necessidade de VPN.

## 📚 Notebooks Disponíveis

### 1. **rm4health_analise_geral.ipynb** 🏥
**Análise completa e exploratória dos dados**
- ✅ Visão geral de todos os dados
- ✅ Análise demográfica dos participantes  
- ✅ Estatísticas descritivas
- ✅ Visualizações interativas
- ✅ Comparação entre grupos
- ✅ Resumo executivo

**Para quem:** Pesquisadores que querem uma visão completa dos dados

### 2. **rm4health_analise_sono.ipynb** 😴
**Análise especializada da qualidade do sono**
- ✅ Avaliação do Pittsburgh Sleep Quality Index (PSQI)
- ✅ Padrões de horário de dormir e acordar
- ✅ Problemas de sono mais comuns
- ✅ Correlações com outras variáveis de saúde
- ✅ Comparação entre grupos
- ✅ Recomendações específicas

**Para quem:** Especialistas em medicina do sono e pesquisadores focados em qualidade do sono

### 3. **rm4health_analise_medicacao.ipynb** 💊
**Análise detalhada de adesão medicamentosa**
- ✅ Taxa de adesão medicamentosa
- ✅ Padrões de horários de medicação
- ✅ Razões para não adesão
- ✅ Análise temporal de esquecimentos
- ✅ Correlações com idade e condições de saúde
- ✅ Estratégias de melhoria

**Para quem:** Farmacêuticos clínicos e pesquisadores em adesão terapêutica

## 🚀 Como Usar

### Pré-requisitos
1. Conta no Google (para acessar Google Colab)
2. Arquivo `redcap_data.csv` com os dados do projeto

### Passo a Passo

1. **Abrir no Google Colab:**
   - Acesse [colab.research.google.com](https://colab.research.google.com)
   - Clique em "Upload" e selecione o notebook desejado
   - Ou use o link direto: `https://colab.research.google.com/github/[seu-repo]/notebooks_colab/[nome-notebook]`

2. **Upload dos dados:**
   - Execute a célula de upload de dados
   - Selecione o arquivo `redcap_data.csv`
   - Aguarde o carregamento ser concluído

3. **Executar análise:**
   - Execute as células sequencialmente (`Ctrl+Enter`)
   - Ou execute tudo: `Runtime > Run all`
   - Aguarde os resultados e visualizações

4. **Download dos resultados:**
   - Os notebooks geram arquivos de resumo em JSON/CSV
   - Download automático dos resultados ao final

## 📊 Dados Necessários

Os notebooks esperam um arquivo CSV com as seguintes características:

### Colunas Principais
- `participant_code`: Código do participante
- `participant_group`: Grupo (Residentes/Comunidade)
- `sex`: Gênero
- `birth_year`: Ano de nascimento
- `education_level`: Nível educacional

### Colunas de Sono (para análise especializada)
- `sleep_quality`: Qualidade do sono percebida
- `sleep_hours`: Horas de sono por noite
- `usual_bedtime`: Horário habitual de deitar
- `trouble_falling_asleep`: Dificuldade para adormecer
- `waking_up_night`: Acordar durante a noite
- E outras variáveis do PSQI

### Colunas de Medicação (para análise especializada)
- `took_medications_yesterday`: Tomou medicação ontem
- `medication_nonadherence_reason`: Razão para não adesão
- `forgot_medication_week`: Esquecimentos na semana
- `medication_frequency_day`: Frequência diária
- E outras variáveis de adesão

## 📈 Resultados Gerados

Cada notebook produz:

### Visualizações Interativas
- 📊 Gráficos de barras e pizza
- 📈 Histogramas e box plots
- 🗺️ Matrizes de correlação
- 📋 Tabelas de contingência

### Arquivos de Saída
- **JSON**: Resumo das principais métricas
- **CSV**: Estatísticas descritivas detalhadas
- **HTML**: Gráficos salvos (quando aplicável)

### Insights e Recomendações
- 🎯 Principais descobertas
- 💡 Recomendações baseadas em evidências
- ⚠️ Alertas para padrões preocupantes
- ✅ Pontos fortes identificados

## 🔧 Personalização

### Modificar Análises
Os notebooks são modulares e podem ser facilmente modificados:

```python
# Exemplo: Adicionar nova análise
nova_variavel = df['nova_coluna'].value_counts()
print("Nova Análise:", nova_variavel)
```

### Adicionar Visualizações
```python
# Exemplo: Novo gráfico
import plotly.express as px
fig = px.bar(df, x='variavel', y='count')
fig.show()
```

### Filtrar Dados
```python
# Exemplo: Analisar apenas um grupo
residentes = df[df['participant_group'] == 'Residentes']
# Continuar análise com 'residentes'
```

## 🤝 Compartilhamento

### Para Colegas
1. Compartilhe o link do notebook no Google Colab
2. Forneça o arquivo CSV de dados
3. Inclua estas instruções

### Para Publicação
1. Exporte resultados para PDF/HTML
2. Salve gráficos como imagens
3. Documente metodologia utilizada

## 🔒 Segurança dos Dados

### ⚠️ Importante
- Os notebooks processam dados localmente no Google Colab
- Dados não são armazenados permanentemente no Google
- Sempre delete dados sensíveis após uso
- Use apenas dados anonimizados

### Boas Práticas
- Não compartilhe notebooks com dados incluídos
- Faça backup dos resultados importantes
- Remova dados da sessão após análise
- Use códigos de participante, não nomes

## 📞 Suporte

### Problemas Comuns

**Erro de upload:**
```
Solução: Verifique se o arquivo é CSV válido e tem as colunas esperadas
```

**Gráficos não aparecem:**
```
Solução: Execute novamente a célula ou reinicie o runtime
```

**Memória insuficiente:**
```
Solução: Use Runtime > Factory reset runtime ou reduza tamanho dos dados
```

### Contato
Para dúvidas técnicas ou sugestões de melhorias, contate a equipe do projeto RM4Health.

---

📅 **Última atualização:** Dezembro 2024  
🔬 **Desenvolvido para:** Projeto RM4Health - FMUP  
💻 **Compatível com:** Google Colab, Jupyter Notebook local
