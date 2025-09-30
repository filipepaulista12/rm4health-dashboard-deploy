#!/usr/bin/env python3
"""
Script para extrair dados da API do REDCap e criar base de dados local
"""

import json
import csv
import pandas as pd
from redcap_client import REDCapClient
from datetime import datetime
import os

def extract_redcap_data():
    """Extrai todos os dados da API e salva em formatos locais"""
    
    print("🔄 Iniciando extração de dados do REDCap...")
    
    try:
        # Conectar à API
        client = REDCapClient()
        print("✅ Cliente REDCap conectado")
        
        # Extrair dados em diferentes formatos
        print("\n📊 Extraindo dados RAW...")
        raw_data = client.get_records(raw_or_label='raw')
        print(f"   → {len(raw_data)} registros extraídos (raw)")
        
        print("\n🏷️  Extraindo dados LABELED...")
        labeled_data = client.get_records(raw_or_label='label')
        print(f"   → {len(labeled_data)} registros extraídos (labeled)")
        
        # Extrair metadados
        print("\n🔧 Extraindo metadados...")
        metadata = client.get_metadata()
        print(f"   → {len(metadata)} campos de metadados")
        
        # Extrair instrumentos (se disponível)
        print("\n📋 Extraindo informações de instrumentos...")
        try:
            instruments = client.get_instruments()
            print(f"   → {len(instruments)} instrumentos encontrados")
        except:
            instruments = []
            print("   → Usando lista vazia (método não disponível)")
        
        # Criar timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salvar em JSON
        print("\n💾 Salvando em JSON...")
        data_structure = {
            'extraction_date': datetime.now().isoformat(),
            'total_records': len(raw_data),
            'data_raw': raw_data,
            'data_labeled': labeled_data,
            'metadata': metadata,
            'instruments': instruments
        }
        
        with open(f'redcap_data_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(data_structure, f, ensure_ascii=False, indent=2, default=str)
        print(f"   ✅ JSON salvo: redcap_data_{timestamp}.json")
        
        # Salvar dados principais em CSV
        print("\n📄 Salvando em CSV...")
        df_raw = pd.DataFrame(raw_data)
        df_labeled = pd.DataFrame(labeled_data)
        
        df_raw.to_csv(f'redcap_raw_{timestamp}.csv', index=False, encoding='utf-8')
        df_labeled.to_csv(f'redcap_labeled_{timestamp}.csv', index=False, encoding='utf-8')
        
        print(f"   ✅ CSV RAW salvo: redcap_raw_{timestamp}.csv")
        print(f"   ✅ CSV LABELED salvo: redcap_labeled_{timestamp}.csv")
        
        # Salvar metadados em CSV
        df_metadata = pd.DataFrame(metadata)
        df_metadata.to_csv(f'redcap_metadata_{timestamp}.csv', index=False, encoding='utf-8')
        print(f"   ✅ Metadados salvos: redcap_metadata_{timestamp}.csv")
        
        # Criar arquivo de configuração
        config_data = {
            'last_extraction': datetime.now().isoformat(),
            'files': {
                'json_file': f'redcap_data_{timestamp}.json',
                'raw_csv': f'redcap_raw_{timestamp}.csv',
                'labeled_csv': f'redcap_labeled_{timestamp}.csv',
                'metadata_csv': f'redcap_metadata_{timestamp}.csv'
            },
            'stats': {
                'total_records': len(raw_data),
                'total_fields': len(metadata),
                'total_instruments': len(instruments)
            }
        }
        
        with open('local_data_config.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        print("\n🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📊 Total de registros: {len(raw_data)}")
        print(f"🔧 Total de campos: {len(metadata)}")
        print(f"📋 Total de instrumentos: {len(instruments)}")
        
        return config_data
        
    except Exception as e:
        print(f"❌ Erro na extração: {e}")
        return None

if __name__ == "__main__":
    extract_redcap_data()
