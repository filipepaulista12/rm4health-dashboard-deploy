#!/usr/bin/env python3
"""
Cliente REDCap Local - Versão SEM pandas para contornar problemas de build
"""
import json
import os
from datetime import datetime

class LocalREDCapClientSimple:
    """Cliente simples que usa apenas JSON, sem pandas"""
    
    def __init__(self):
        self.config_file = 'local_data_config.json'
        self.load_config()
        self.load_data()
    
    def load_config(self):
        """Carrega configuração dos arquivos de dados"""
        if not os.path.exists(self.config_file):
            print(f"[WARNING] Arquivo de configuracao nao encontrado: {self.config_file}")
            print("[INFO] Criando configuracao padrao...")
            self.create_default_config()
            return
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def load_data(self):
        """Carrega todos os dados em memória"""
        print("[INFO] Carregando dados locais...")
        
        # Carregar JSON completo
        json_file = self.config['files']['json_file']
        
        if not os.path.exists(json_file):
            print(f"[WARNING] Arquivo de dados nao encontrado: {json_file}")
            print("[INFO] Usando dados padrao...")
            # Se não existe, usar dados já criados no create_default_config
            if hasattr(self, 'full_data'):
                return
            else:
                # Criar dados de emergência
                self.full_data = {
                    "data_raw": [],
                    "data_labeled": [],
                    "metadata": []
                }
                return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.full_data = json.load(f)
            print(f"[OK] Dados carregados: {len(self.full_data.get('data_raw', []))} registros")
        except Exception as e:
            print(f"[ERROR] Erro ao carregar dados: {e}")
            print("[INFO] Usando dados de emergencia...")
            self.full_data = {
                "data_raw": [],
                "data_labeled": [],
                "metadata": []
            }
    
    def test_connection(self):
        """Simula teste de conexão"""
        return True
    
    def get_records(self, raw_or_label='label', **kwargs):
        """Retorna registros (simulando a API)"""
        print(f"[INFO] Conectando a base local...")
        
        if raw_or_label == 'raw':
            data = self.full_data.get('data_raw', [])
        else:
            data = self.full_data.get('data_labeled', [])
        
        print(f"[OK] Base local conectada! {len(data)} registros encontrados")
        return data
    
    def get_metadata(self):
        """Retorna metadados"""
        return self.full_data.get('metadata', [])
    
    def get_project_info(self):
        """Retorna informações do projeto"""
        return {
            'project_title': 'RM4Health - Remote Monitoring for Elderly Health (LOCAL)',
            'record_count': self.config['stats']['total_records'],
            'field_count': self.config['stats']['total_fields'],
            'last_extraction': self.config['last_extraction']
        }
    
    def get_stats(self):
        """Retorna estatísticas dos dados"""
        return {
            'total_records': len(self.full_data.get('data_raw', [])),
            'total_fields': len(self.full_data.get('metadata', [])),
            'extraction_date': self.config['last_extraction'],
            'data_source': 'LOCAL_FILES_SIMPLE'
        }
    
    def create_default_config(self):
        """Cria configuração padrão e dados de exemplo mínimos"""
        print("📝 Criando dados de exemplo mínimos para demonstração...")
        
        # Configuração padrão
        self.config = {
            "last_extraction": datetime.now().isoformat(),
            "files": {
                "json_file": "demo_data.json"
            },
            "stats": {
                "total_records": 10,
                "total_fields": 20
            }
        }
        
        # Dados de exemplo mínimos
        demo_data = {
            "data_raw": [
                {"record_id": f"DEMO_{i:03d}", "age": 65+i, "gender": "Female" if i%2 else "Male"} 
                for i in range(10)
            ],
            "data_labeled": [
                {"record_id": f"DEMO_{i:03d}", "age": 65+i, "gender": "Female" if i%2 else "Male"} 
                for i in range(10)
            ],
            "metadata": [
                {"field_name": "record_id", "form_name": "demographics", "field_label": "Record ID"},
                {"field_name": "age", "form_name": "demographics", "field_label": "Age"},
                {"field_name": "gender", "form_name": "demographics", "field_label": "Gender"}
            ]
        }
        
        # Salvar arquivos
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        
        with open("demo_data.json", 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, indent=2)
        
        self.full_data = demo_data
        print("✅ Dados de exemplo criados com sucesso!")
