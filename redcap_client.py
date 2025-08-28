import requests
import json
from config import Config

class REDCapClient:
    def __init__(self):
        self.url = Config.REDCAP_URL
        self.token = Config.REDCAP_TOKEN
        self.timeout = Config.REDCAP_TIMEOUT
    
    def get_records(self, raw_or_label='label'):
        """Busca todos os registros da API REDCap"""
        data = {
            'token': self.token,
            'content': 'record',
            'action': 'export',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'rawOrLabel': raw_or_label,
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
        }
        
        try:
            print(f"🔌 Conectando à API: {self.url}")
            response = requests.post(self.url, data=data, timeout=self.timeout)
            response.raise_for_status()
            records = response.json()
            print(f"✅ API conectada com sucesso! {len(records)} registros encontrados")
            return records
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            return []
    
    def get_metadata(self):
        """Busca metadados dos campos"""
        data = {
            'token': self.token,
            'content': 'metadata',
            'format': 'json',
            'returnFormat': 'json'
        }
        
        try:
            response = requests.post(self.url, data=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar metadados: {e}")
            return []
    
    def test_connection(self):
        """Testa a conexão com a API"""
        try:
            data = {
                'token': self.token,
                'content': 'project',
                'format': 'json',
                'returnFormat': 'json'
            }
            response = requests.post(self.url, data=data, timeout=self.timeout)
            response.raise_for_status()
            project_info = response.json()
            print(f"✅ Conexão testada! Projeto: {project_info.get('project_title', 'N/A')}")
            return True
        except Exception as e:
            print(f"❌ Falha no teste de conexão: {e}")
            return False
