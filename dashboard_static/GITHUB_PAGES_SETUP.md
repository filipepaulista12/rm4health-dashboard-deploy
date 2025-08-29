#  Como Configurar GitHub Pages para o Dashboard RM4Health

##  Passos para Ativar GitHub Pages

### 1. Acessar Configurações do Repositório
- Vá para: https://github.com/filipepaulista12/rm4health-dashboard-deploy
- Clique na aba **Settings**

### 2. Configurar GitHub Pages
- No menu lateral esquerdo, clique em **Pages**
- Em **Source**, selecionar **Deploy from a branch**
- Em **Branch**, selecionar **github-pages-dashboard**
- Em **Folder**, selecionar **/ (root)**
- Clicar em **Save**

### 3. Aguardar Deploy
- GitHub vai processar automaticamente
- Processo demora 2-5 minutos
- URL final será: `https://filipepaulista12.github.io/rm4health-dashboard-deploy/dashboard_static/`

##  URLs do Dashboard

### URL Principal
```
https://filipepaulista12.github.io/rm4health-dashboard-deploy/dashboard_static/
```

### URLs das Páginas Específicas
```
https://filipepaulista12.github.io/rm4health-dashboard-deploy/dashboard_static/medicacao.html
https://filipepaulista12.github.io/rm4health-dashboard-deploy/dashboard_static/sono.html  
https://filipepaulista12.github.io/rm4health-dashboard-deploy/dashboard_static/servicos.html
https://filipepaulista12.github.io/rm4health-dashboard-deploy/dashboard_static/participantes.html
```

##  Verificar se Funcionou

### 1. Indicadores de Sucesso
-  Página carrega sem erro 404
-  CSS e JavaScript carregam corretamente
-  Dados do CSV aparecem nas tabelas
-  Gráficos renderizam
-  Navegação entre páginas funciona

### 2. Testar Funcionalidades
- **Dashboard Principal:** Estatísticas e gráficos aparecem
- **Medicação:** Tabela de aderência popula
- **Sono:** Gráfico radar PSQI funciona
- **Serviços:** Dados de utilização carregam
- **Participantes:** Lista filtros e paginação

##  Solução de Problemas

### Problema: Página 404
**Solução:** Verificar se branch `github-pages-dashboard` foi selecionado nas configurações

### Problema: CSS não carrega
**Solução:** URLs estão configurados como relativos, deve funcionar automaticamente

### Problema: Dados não aparecem
**Solução:** Verificar se `rm4health_dados_reais.csv` está no repositório

### Problema: JavaScript erros
**Solução:** Verificar console do browser (F12) para debug

##  Monitoramento

### GitHub Actions
- GitHub Pages usa Actions automáticos
- Ver status em: Repository  Actions tab
- Builds aparecem como "pages-build-deployment"

### Analytics (Opcional)
- Adicionar Google Analytics no `index.html` se necessário
- Tracking de visitantes automático do GitHub

##  Atualizações

### Para Atualizar Dados
1. Substituir `dashboard_static/data/rm4health_dados_reais.csv`
2. Commit e push para `github-pages-dashboard`
3. GitHub Pages atualiza automaticamente em ~5 minutos

### Para Modificar Páginas
1. Editar arquivos HTML/CSS/JS
2. Commit e push para `github-pages-dashboard`
3. Aguardar rebuild automático

##  Resultado Final

Um dashboard completamente funcional e público que:
-  Replica exatamente as funções do sistema original
-  Usa dados reais do REDCap
-  Funciona sem VPN ou autenticação
-  Atualiza com novos commits
-  É acessível de qualquer lugar

##  Suporte

Se algo não funcionar:
1. Verificar console do browser (F12)
2. Checar status do GitHub Pages nas Settings
3. Validar que branch correto está selecionado
4. Aguardar 5-10 minutos após mudanças

---
** Dashboard RM4Health agora disponível publicamente via GitHub Pages!**
