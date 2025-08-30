import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Modo de operação - LOCAL ou API
    USE_LOCAL_DATA = True  # Mudado para True para usar dados locais
    
    # API REDCap (mantido para compatibilidade)
    REDCAP_URL = "https://redcap.med.up.pt/redcap/api/"
    REDCAP_TOKEN = "80A76D08B815458E054C3687D282E8DF"
    REDCAP_TIMEOUT = 30
    
    # Arquivos de dados locais
    LOCAL_DATA_CONFIG = "local_data_config.json"
    
    # Projeto
    PROJECT_NAME = "RM4Health"
    PROJECT_TITLE = "Remote Monitoring 4 Health"
    PROJECT_SUBTITLE = "Sistema de Monitoramento Remoto de Saúde"
    
    # Dashboard
    PARTICIPANTS_COUNT = 23
    TOTAL_RECORDS = 512
    TOTAL_VARIABLES = 247
    AVERAGE_AGE = 85.9
    
    # Aparência
    PRIMARY_COLOR = "#2c5aa0"
    SECONDARY_COLOR = "#48c9b0"
    CHART_HEIGHT = 400
    CHART_WIDTH = 600
