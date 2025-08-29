#  TESTE DE CSV - RM4Health Dashboard

Este dashboard **AGORA USA DADOS REAIS** do arquivo `rm4health_dados_reais.csv` em vez de dados simulados.

##  CORREÇÕES IMPLEMENTADAS

###  Problema Resolvido: CSV Real
- **ANTES**: Dashboard mostrava "dados mockados"
- **DEPOIS**: Carrega e processa dados reais do REDCap (514 colunas)
- **Arquivo**: `dashboard_static/data/rm4health_dados_reais.csv`

###  Melhorias Técnicas
1. **Carregamento Robusto**: Múltiplas estratégias de fetch
2. **Algoritmos Reais**: Implementação científica dos notebooks
3. **Debug Avançado**: Logs detalhados para troubleshooting
4. **Tratamento de Erros**: Fallbacks inteligentes

##  Como Testar

### 1. Teste Rápido
Abra: `test_csv.html` para verificar se o CSV carrega corretamente.

### 2. Teste Completo
1. Abra `index.html`
2. Abra Console do navegador (F12)
3. Procure por logs: ` Loading CSV data from:`
4. Deve ver: ` CSV loaded successfully`

### 3. Debug Manual
```javascript
// No console do navegador:
debugRM4Health();
debugRM4Dashboard();
```

##  Algoritmos Implementados

###  Medicação (Sistema 4-pontos)
- **Sim** = 4 pontos
- **Às vezes** = 2 pontos  
- **Raramente** = 1 ponto
- **Não** = 0 pontos

###  Sono (PSQI Científico)
- Qualidade subjetiva
- Latência do sono
- Duração do sono
- Pontuação: 0-21 (menor = melhor)

###  Utilização de Serviços
- **Alto utilizador**: Percentil 75 (P75)
- Consultas + Urgências + Internamentos
- Identificação baseada em dados reais

###  Deterioração da Saúde
- Múltiplos fatores de risco
- Pontuação ponderada
- Classificação: Baixo/Médio/Alto

##  Troubleshooting

### Problema: "Chart is not defined"
**Solução**: Verificar ordem de carregamento dos scripts:
1. Bootstrap
2. Chart.js
3. PapaParse
4. data-loader.js
5. dashboard.js

### Problema: "Dados mockados"
**Soluções**:
1. Executar `test_csv.html` primeiro
2. Verificar console para erros de fetch
3. Confirmar que CSV existe: `data/rm4health_dados_reais.csv`
4. Limpar cache do navegador

### Problema: CORS Error
**GitHub Pages**: Normalmente resolve automaticamente
**Local**: Usar servidor HTTP (`python -m http.server`)

##  Estrutura de Arquivos
```
dashboard_static/
 index.html              # Dashboard principal  
 medicacao.html          # Análise medicação
 sono.html              # Análise sono (PSQI)
 servicos.html          # Utilização serviços
 test_csv.html          #  TESTE DE CSV
 data/
    rm4health_dados_reais.csv  #  DADOS REAIS
 js/
    data-loader.js     #  CORRIGIDO - Carrega CSV real
    dashboard.js       #  CORRIGIDO - Usa dados reais
    charts.js          # Configurações Chart.js
 css/
     dashboard.css      # Estilos
```

##  Próximos Passos

1. **Testar**: Abrir `test_csv.html` para confirmar CSV
2. **Verificar**: Dashboard principal com dados reais
3. **Navegar**: Entre páginas de análise
4. **Debug**: Usar funções de debug se necessário

---

**IMPORTANTE**: Este dashboard agora processa dados científicos reais!
Os algoritmos implementados seguem as mesmas especificações dos notebooks originais.
