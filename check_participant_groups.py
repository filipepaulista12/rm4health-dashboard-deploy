#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config
import requests
import pandas as pd
from collections import Counter

def check_participant_groups():
    """Verifica os valores reais do campo participant_group"""
    try:
        # Obter dados dos participantes
        data = {
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
        
        print("🔍 Obtendo dados dos participantes...")
        response = requests.post(Config.REDCAP_URL, data=data)
        response.raise_for_status()
        records = response.json()
        
        print(f"📊 Total de registros: {len(records)}")
        
        # Verificar valores do campo participant_group
        participant_groups = []
        participant_codes = []
        
        for record in records:
            group = record.get('participant_group', '')
            code = record.get('participant_code_estudo', record.get('participant_code', ''))
            
            if group:
                participant_groups.append(group)
            if code:
                participant_codes.append(code)
        
        print(f"\n📋 ANÁLISE DO CAMPO 'participant_group':")
        print("=" * 50)
        
        if participant_groups:
            group_counts = Counter(participant_groups)
            print("Distribuição dos grupos:")
            for group, count in group_counts.items():
                group_desc = {
                    'a': 'Residente (Grupo A)',
                    'b': 'Não-Residente (Grupo B)', 
                    'c': 'Cuidador informal (Grupo C)',
                    'd': 'Cuidador formal (Grupo D)'
                }.get(group, f'Desconhecido ({group})')
                
                print(f"  📌 {group}: {count} - {group_desc}")
        else:
            print("❌ Nenhum valor encontrado no campo 'participant_group'")
            
        print(f"\n📝 ANÁLISE DOS CÓDIGOS DOS PARTICIPANTES:")
        print("=" * 50)
        if participant_codes:
            print(f"  📊 Participantes únicos: {len(set(participant_codes))}")
            print(f"  📊 Primeiros códigos: {participant_codes[:10]}")
        else:
            print("❌ Nenhum código de participante encontrado")
            
        # Verificar alguns registros específicos
        print(f"\n🔍 AMOSTRA DE REGISTROS (primeiros 5):")
        print("=" * 50)
        for i, record in enumerate(records[:5]):
            print(f"\n📋 Registro {i+1}:")
            print(f"  - participant_code: {record.get('participant_code', 'N/A')}")
            print(f"  - participant_code_estudo: {record.get('participant_code_estudo', 'N/A')}")
            print(f"  - participant_group: {record.get('participant_group', 'N/A')}")
            
        return records
        
    except Exception as e:
        print(f"❌ Erro ao verificar grupos de participantes: {e}")
        return []

if __name__ == "__main__":
    check_participant_groups()
