# RM4Health Dashboard - GitHub Pages

Este é um dashboard estático que replica as funcionalidades do sistema RM4Health original, mas usando dados do CSV ao invés da API do REDCap.

##  Acesso ao Dashboard

**GitHub Pages URL:** https://filipepaulista12.github.io/rm4health-dashboard-deploy/dashboard_static/

##  Funcionalidades

### Dashboard Principal (index.html)
- Estatísticas gerais dos participantes
- Gráficos de tendência de aderência
- Distribuição por idade
- Participantes de alto risco
- Alertas em tempo real

### Páginas Especializadas
- **Medicação (medicacao.html):** Análise completa de aderência com algoritmo real de 4-pontos
- **Sono (sono.html):** Análise PSQI científica com 7 componentes [Em desenvolvimento]
- **Serviços de Saúde (servicos.html):** Utilização e preditores [Em desenvolvimento]
- **Participantes (participantes.html):** Lista detalhada [Em desenvolvimento]

##  Tecnologias

- **Frontend:** HTML5, CSS3, JavaScript ES6+
- **CSS Framework:** Bootstrap 5.3.0
- **Ícones:** Font Awesome 6.4.0
- **Gráficos:** Chart.js 4.3.0
- **CSV Parsing:** PapaParse 5.4.1
- **Dados:** CSV real do REDCap (514 colunas, dados reais anonimizados)

##  Algoritmos Implementados

### Medicação (Replicação Exata dos Notebooks)
```javascript
// Sistema de scoring 4-pontos
switch (response) {
    case 'Sim': score = 4; break;
    case 'Às vezes': score = 2; break;
    case 'Raramente': score = 1; break;
    case 'Não': score = 0; break;
}
```

### Detecção de Deterioração da Saúde
```javascript
// Algoritmo de risco
if (no_medication) riskScore += 25;
if (poor_sleep) riskScore += 20;
if (sleep_hours < 5) riskScore += 15;
if (emergency_visits > 2) riskScore += 30;

// Classificação: Alto (50), Médio (25-49), Baixo (<25)
```

##  Estrutura de Arquivos

```
dashboard_static/
 index.html              # Página principal
 medicacao.html           # Análise de medicação
 sono.html               # Análise PSQI [Planejado]
 servicos.html           # Serviços de saúde [Planejado]
 participantes.html      # Lista participantes [Planejado]
 css/
    dashboard.css       # Estilos personalizados
 js/
    data-loader.js      # Carregamento e processamento CSV
    dashboard.js        # Lógica principal
    charts.js          # Gráficos avançados
 data/
     rm4health_dados_reais.csv  # Dados REDCap reais
```

##  Diferenças do Sistema Original

| Aspecto | Sistema Original | GitHub Pages |
|---------|------------------|--------------|
| **Dados** | API REDCap (tempo real) | CSV estático |
| **Backend** | Python/Flask/Streamlit | JavaScript puro |
| **Autenticação** | VPN + API Key | Público |
| **Atualização** | Automática | Manual (CSV) |
| **Algoritmos** |  Idênticos |  Idênticos |

##  Como Atualizar Dados

1. Exportar novo CSV do REDCap
2. Substituir `data/rm4health_dados_reais.csv`
3. Commit e push para GitHub
4. GitHub Pages atualiza automaticamente

##  Responsivo

-  Desktop (1200px+)
-  Tablet (768px-1199px)
-  Mobile (<=767px)

##  Design

- **Cores:** Bootstrap 5 color system
- **Ícones:** Font Awesome 6.4.0
- **Gráficos:** Chart.js com paleta personalizada
- **Animações:** CSS transitions e Chart.js animations
- **Tema:** Limpo, profissional, científico

##  Performance

- **Carregamento:** <3 segundos (CSV ~2MB)
- **Responsividade:** <200ms para interações
- **Gráficos:** Hardware-accelerated Canvas
- **CDN:** Bootstrap, Font Awesome, Chart.js via CDN

##  Compatibilidade

-  Chrome 90+
-  Firefox 88+
-  Safari 14+
-  Edge 90+

##  Dados Utilizados

- **Fonte:** RM4HealthRemoteMonit_DATA_LABELS_2025-08-11_0937.csv
- **Colunas:** 514 variáveis reais
- **Participantes:** Dados reais anonimizados
- **Algoritmos:** Exatamente iguais aos notebooks científicos

---

**Desenvolvido para o projeto RM4Health - FMUP**  
*Dashboard estático com funcionalidades reais para acesso sem VPN*
