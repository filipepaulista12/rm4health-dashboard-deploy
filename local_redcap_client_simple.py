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
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def load_data(self):
        """Carrega todos os dados em memória"""
        print("📂 Carregando dados locais...")
        
        # Carregar JSON completo
        json_file = self.config['files']['json_file']
        with open(json_file, 'r', encoding='utf-8') as f:
            self.full_data = json.load(f)
        
        print(f"✅ Dados carregados: {len(self.full_data.get('data_raw', []))} registros")
    
    def test_connection(self):
        """Simula teste de conexão"""
        return True
    
    def get_records(self, raw_or_label='label', **kwargs):
        """Retorna registros (simulando a API)"""
        print(f"🔌 Conectando à base local...")
        
        if raw_or_label == 'raw':
            data = self.full_data.get('data_raw', [])
        else:
            data = self.full_data.get('data_labeled', [])
        
        print(f"✅ Base local conectada! {len(data)} registros encontrados")
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
