#!/usr/bin/env python3
"""
Cliente REDCap Local - Substitui a API usando dados estáticos
Mantém a mesma interface da classe original
"""

import json
import pandas as pd
import os
from datetime import datetime

class LocalREDCapClient:
    """Cliente que simula a API do REDCap usando dados locais"""
    
    def __init__(self):
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, 'local_data_config.json')
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
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Carregar JSON completo
        json_file = os.path.join(script_dir, self.config['files']['json_file'])
        with open(json_file, 'r', encoding='utf-8') as f:
            self.full_data = json.load(f)
        
        # Carregar CSVs
        self.df_raw = pd.read_csv(os.path.join(script_dir, self.config['files']['raw_csv']))
        self.df_labeled = pd.read_csv(os.path.join(script_dir, self.config['files']['labeled_csv']))
        self.df_metadata = pd.read_csv(os.path.join(script_dir, self.config['files']['metadata_csv']))
        
        print(f"✅ Dados carregados: {len(self.df_raw)} registros")
    
    def test_connection(self):
        """Simula teste de conexão"""
        return True
    
    def get_records(self, raw_or_label='label', **kwargs):
        """Retorna registros (simulando a API)"""
        print(f"🔌 Conectando à base local...")
        
        if raw_or_label == 'raw':
            data = self.full_data['data_raw']
        else:
            data = self.full_data['data_labeled']
        
        print(f"✅ Base local conectada! {len(data)} registros encontrados")
        return data
    
    def get_metadata(self):
        """Retorna metadados"""
        return self.full_data['metadata']
    
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
            'total_records': len(self.df_raw),
            'total_fields': len(self.df_metadata),
            'extraction_date': self.config['last_extraction'],
            'data_source': 'LOCAL_FILES'
        }
