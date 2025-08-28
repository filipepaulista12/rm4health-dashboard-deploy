#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config
import requests
import json
import pandas as pd

def get_redcap_field_names():
    """Obtém todos os nomes de campos do REDCap"""
    try:
        # Obter metadados do projeto
        metadata_data = {
            'token': Config.REDCAP_TOKEN,
            'content': 'metadata',
            'format': 'json',
            'returnFormat': 'json'
        }
        
        print("🔍 Obtendo metadados do REDCap...")
        metadata_response = requests.post(Config.REDCAP_URL, data=metadata_data)
        metadata_response.raise_for_status()
        metadata = metadata_response.json()
        
        print(f"📊 Total de campos encontrados: {len(metadata)}")
        
        # Procurar campos relacionados à residência/moradia
        residence_related = []
        all_fields = []
        
        for field in metadata:
            field_name = field.get('field_name', '')
            field_label = field.get('field_label', '')
            field_type = field.get('field_type', '')
            choices = field.get('select_choices_or_calculations', '')
            
            all_fields.append({
                'name': field_name,
                'label': field_label,
                'type': field_type,
                'choices': choices
            })
            
            # Buscar campos relacionados à residência/moradia
            keywords = ['resid', 'mora', 'casa', 'lar', 'living', 'home', 'care', 'facility', 'nursing']
            if any(keyword in field_name.lower() or keyword in field_label.lower() for keyword in keywords):
                residence_related.append({
                    'name': field_name,
                    'label': field_label,
                    'type': field_type,
                    'choices': choices
                })
        
        print("\n🏠 CAMPOS RELACIONADOS À RESIDÊNCIA/MORADIA:")
        print("=" * 60)
        for field in residence_related:
            print(f"📌 Campo: {field['name']}")
            print(f"   Label: {field['label']}")
            print(f"   Tipo: {field['type']}")
            if field['choices']:
                print(f"   Opções: {field['choices']}")
            print()
        
        # Também vamos obter alguns registros de exemplo para ver os dados reais
        print("\n📋 OBTENDO DADOS DE EXEMPLO...")
        record_data = {
            'token': Config.REDCAP_TOKEN,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'csvDelimiter': '',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
        }
        
        records_response = requests.post(Config.REDCAP_URL, data=record_data)
        records_response.raise_for_status()
        records = records_response.json()
        
        print(f"📊 Total de registros: {len(records)}")
        
        # Verificar os campos de residência nos registros reais
        if records and residence_related:
            print("\n🔍 VALORES REAIS NOS CAMPOS DE RESIDÊNCIA:")
            print("=" * 60)
            
            for field in residence_related[:3]:  # Apenas primeiros 3 campos
                field_name = field['name']
                values = []
                
                for record in records[:20]:  # Apenas primeiros 20 registros
                    if field_name in record and record[field_name]:
                        values.append(record[field_name])
                
                unique_values = list(set(values))
                print(f"📌 {field_name}: {unique_values[:10]}")  # Primeiros 10 valores únicos
        
        # Salvar informações para análise posterior
        with open('field_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({
                'all_fields': all_fields,
                'residence_related': residence_related,
                'sample_records': records[:5] if records else []
            }, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Análise salva em 'field_analysis.json'")
        
        return all_fields, residence_related
        
    except Exception as e:
        print(f"❌ Erro ao analisar campos: {e}")
        return [], []

if __name__ == "__main__":
    get_redcap_field_names()
