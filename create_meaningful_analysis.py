#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config
import requests
import pandas as pd
from collections import Counter
import json

def create_meaningful_residence_analysis():
    """Cria uma análise mais significativa baseada nos dados reais do REDCap"""
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
        
        print("🔍 Obtendo dados completos do REDCap...")
        response = requests.post(Config.REDCAP_URL, data=data)
        response.raise_for_status()
        records = response.json()
        
        df = pd.DataFrame(records)
        
        # Filtrar participantes únicos
        unique_participants = df[
            (df['participant_code_estudo'].notna()) & 
            (df['participant_code_estudo'] != '')
        ].copy()
        
        print(f"📊 Participantes únicos encontrados: {len(unique_participants)}")
        
        # Separar grupos
        residents = unique_participants[unique_participants['participant_group'] == 'a'].copy()  # Grupo A
        non_residents = unique_participants[unique_participants['participant_group'] == 'b'].copy()  # Grupo B
        
        print(f"🏠 Residentes (Grupo A): {len(residents)}")
        print(f"🏡 Não-Residentes (Grupo B): {len(non_residents)}")
        
        if len(residents) == 0 or len(non_residents) == 0:
            print("⚠️  Um dos grupos está vazio. Análise comparativa não é possível.")
            return
        
        # Analisar campos disponíveis com dados
        print("\n📋 ANÁLISE DE CAMPOS COM DADOS:")
        print("=" * 60)
        
        meaningful_fields = []
        
        for column in unique_participants.columns:
            # Contar quantos valores não-vazios existem
            non_empty_count = unique_participants[column].notna().sum()
            if non_empty_count > 5:  # Pelo menos 5 valores
                unique_values = unique_participants[column].dropna().nunique()
                if unique_values > 1:  # Mais de um valor único
                    meaningful_fields.append({
                        'field': column,
                        'non_empty': non_empty_count,
                        'unique_values': unique_values,
                        'sample_values': unique_participants[column].dropna().unique()[:5].tolist()
                    })
        
        # Ordenar por quantidade de dados
        meaningful_fields.sort(key=lambda x: x['non_empty'], reverse=True)
        
        print(f"📊 Campos com dados significativos: {len(meaningful_fields)}")
        
        # Mostrar os 20 campos mais relevantes
        for i, field_info in enumerate(meaningful_fields[:20]):
            print(f"   {i+1:2d}. {field_info['field']}: {field_info['non_empty']} valores, {field_info['unique_values']} únicos")
            print(f"       Exemplos: {field_info['sample_values']}")
        
        # Análise específica por grupo
        print(f"\n🔍 COMPARAÇÃO DETALHADA ENTRE GRUPOS:")
        print("=" * 60)
        
        comparison_results = {}
        
        # Campos demográficos básicos
        demographic_fields = ['birth_year', 'sex', 'marital_status', 'education_level']
        
        for field in demographic_fields:
            if field in unique_participants.columns:
                residents_data = residents[field].dropna()
                non_residents_data = non_residents[field].dropna()
                
                if len(residents_data) > 0 and len(non_residents_data) > 0:
                    print(f"\n📊 {field.upper()}:")
                    print(f"   Residentes: {residents_data.value_counts().to_dict()}")
                    print(f"   Não-Residentes: {non_residents_data.value_counts().to_dict()}")
                    
                    comparison_results[field] = {
                        'residents': residents_data.value_counts().to_dict(),
                        'non_residents': non_residents_data.value_counts().to_dict()
                    }
        
        # Campos de saúde
        health_fields = [field_info for field_info in meaningful_fields[:20] 
                        if any(health_term in field_info['field'].lower() for health_term in 
                              ['health', 'pain', 'symptom', 'medication', 'disease', 'condition'])
                        ]
        
        print(f"\n🏥 CAMPOS DE SAÚDE ENCONTRADOS: {len(health_fields)}")
        for field_info in health_fields[:10]:
            field = field_info['field']
            residents_data = residents[field].dropna()
            non_residents_data = non_residents[field].dropna()
            
            if len(residents_data) > 0 and len(non_residents_data) > 0:
                print(f"\n💊 {field}:")
                print(f"   Residentes ({len(residents_data)}): {residents_data.value_counts().head(3).to_dict()}")
                print(f"   Não-Residentes ({len(non_residents_data)}): {non_residents_data.value_counts().head(3).to_dict()}")
        
        # Salvar análise detalhada
        analysis_results = {
            'summary': {
                'total_participants': len(unique_participants),
                'residents': len(residents),
                'non_residents': len(non_residents),
                'meaningful_fields_count': len(meaningful_fields)
            },
            'meaningful_fields': meaningful_fields[:50],  # Top 50 campos
            'demographic_comparison': comparison_results,
            'residents_sample': residents.head(3).to_dict('records'),
            'non_residents_sample': non_residents.head(3).to_dict('records')
        }
        
        with open('detailed_residence_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Análise detalhada salva em 'detailed_residence_analysis.json'")
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_meaningful_residence_analysis()
