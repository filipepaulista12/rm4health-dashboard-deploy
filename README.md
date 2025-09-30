# RM4Health Dashboard - Repositório de Deploy

Sistema de dashboard para análise de dados do projeto RM4Health com integração REDCap.

##  Características

- **Dashboard Web Flask** com interface responsiva
- **Integração REDCap** para dados em tempo real
- **Análises Avançadas** incluindo:
  - Domínios de saúde RM4Health
  - Análise de sono
  - Aderência medicamentosa
  - Explorador de dados interativo
  - Alertas clínicos
  - Analytics avançados
- **Dados Locais** como fallback
- **596 registros** carregados e analisados

##  Pré-requisitos

- Python 3.8+
- Acesso à API REDCap (opcional, funciona com dados locais)

##  Instalação

1. **Clone o repositório:**
`ash
git clone https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
cd rm4health-dashboard-deploy
`

2. **Crie um ambiente virtual:**
`ash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
`

3. **Instale as dependências:**
`ash
pip install -r requirements.txt
`

4. **Configure as variáveis de ambiente:**
`ash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# REDCAP_URL=https://sua-instancia-redcap.com/api/
# REDCAP_TOKEN=seu_token_aqui
`

##  Execução

### Método 1: Script automatizado
`ash
# Execute o script batch (Windows)
EXECUTAR_DASHBOARD.bat
`

### Método 2: Manual
`ash
# Ative o ambiente virtual
.venv\Scripts\activate

# Execute o dashboard
python app.py
`

##  Acesso

Após iniciar, o dashboard estará disponível em:
- **Local:** http://127.0.0.1:5000
- **Rede local:** http://[SEU_IP]:5000

##  Funcionalidades

### Páginas Disponíveis:
- **Dashboard Principal** - Visão geral dos dados
- **Domínios RM4Health** - Análise específica dos domínios de saúde
- **Participantes** - Gestão e visualização de participantes
- **Análise do Sono** - Métricas e padrões de sono
- **Aderência Medicamentosa** - Monitoramento de medicação
- **Explorador de Dados** - Interface interativa para exploração
- **Alertas Clínicos** - Sistema de alertas baseado em dados
- **Analytics** - Análises estatísticas avançadas

##  Segurança

- **Tokens e credenciais** são gerenciados via variáveis de ambiente
- **Dados sensíveis** não são commitados no repositório
- **Fallback local** para funcionamento sem API externa

##  Desenvolvimento

### Estrutura do Projeto:
`
rm4health-dashboard-deploy/
 app.py                      # Aplicação Flask principal
 config.py                   # Configurações
 redcap_client.py           # Cliente REDCap
 templates/                  # Templates HTML
 static/                     # Arquivos estáticos
 .env.example               # Exemplo de configuração
 local_data_config.json     # Dados locais
 EXECUTAR_DASHBOARD.bat     # Script de execução
 requirements.txt           # Dependências Python
 README.md                  # Este arquivo
`

##  Logs e Debug

O sistema inclui logs detalhados:
-  Inicialização de componentes
-  Status de conexões
-  Carregamento de dados
-  Avisos e erros

##  Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

##  Licença

Este projeto está sob licença [Especificar Licença].

---

**Desenvolvido para o projeto RM4Health - FMUP**
