# RM4Health Dashboard

Um dashboard interativo para análise de dados do projeto RM4Health, desenvolvido com Flask e integração com REDCap API.

## 🎯 Funcionalidades

### Análises Disponíveis

1. **📊 Dashboard Principal**
   - Visão geral dos participantes
   - Estatísticas básicas do projeto
   - Navegação para análises específicas

2. **💤 Análise do Sono**
   - Padrões de sono dos participantes
   - Qualidade do sono por grupo
   - Visualizações interativas

3. **💊 Aderência à Medicação**
   - Análise de aderência medicamentosa
   - Comparações por grupo
   - Identificação de padrões

4. **🏥 Utilização de Cuidados de Saúde**
   - Análise de uso de serviços de saúde
   - Padrões de utilização por grupo
   - Métricas de acesso

5. **👥 Análise de Cuidadores**
   - Dados sobre cuidadores informais
   - Impacto no cuidado
   - Correlações importantes

6. **🔍 Qualidade dos Dados**
   - Análise de completude dos dados
   - Identificação de dados em falta
   - Recomendações de qualidade
   - Verificações de consistência temporal

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Acesso à API do REDCap
- Token de API válido

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
cd rm4health-dashboard-deploy
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo `config.py`:
```python
# Substitua pelos seus dados
REDCAP_URL = "sua_url_redcap"
REDCAP_TOKEN = "seu_token_aqui"
```

5. Execute a aplicação:
```bash
python app.py
```

6. Acesse no navegador:
```
http://localhost:5000
```

## 📁 Estrutura do Projeto

```
├── app.py                 # Aplicação principal Flask
├── config.py             # Configurações da aplicação
├── data_processor.py     # Processamento de dados REDCap
├── redcap_client.py      # Cliente para API REDCap
├── requirements.txt      # Dependências Python
├── static/              # Arquivos CSS, JS, imagens
│   ├── css/
│   └── js/
├── templates/           # Templates HTML
│   ├── dashboard.html
│   ├── sleep_analysis.html
│   ├── medication_adherence.html
│   ├── healthcare_utilization.html
│   ├── caregiver_analysis.html
│   └── data_quality.html
└── README.md
```

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` (opcional) ou configure diretamente no `config.py`:

- `REDCAP_URL`: URL da sua instância REDCap
- `REDCAP_TOKEN`: Token de API do projeto RM4Health

### Personalização
O dashboard pode ser personalizado editando:
- Templates HTML em `templates/`
- Estilos CSS em `static/css/`
- Lógica de análise em `data_processor.py`

## 📊 Dados Suportados

O dashboard funciona com dados do projeto RM4Health que incluem:
- Dados demográficos dos participantes
- Informações sobre sono e atividade
- Dados de medicação
- Registros de utilização de cuidados de saúde
- Informações sobre cuidadores

## 🔒 Segurança

- Nunca commit seu token REDCap
- Use variáveis de ambiente em produção
- Configure adequadamente as permissões de API
- Monitore o acesso aos dados

## 🤝 Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Suporte

Para questões sobre o projeto RM4Health ou uso do dashboard:
- Abra uma issue no GitHub
- Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido para o Projeto RM4Health** 🏥✨
