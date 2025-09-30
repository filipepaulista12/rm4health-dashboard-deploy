"""
Script para obter todos os dados do REDCap e identificar campos úteis
"""

from config import Config
import requests
import pandas as pd
import json

def get_all_redcap_data():
    """Obtém todos os dados do REDCap para análise real"""
    
    print("📊 OBTENDO TODOS OS DADOS REAIS DO REDCap")
    print("=" * 50)
    
    try:
        # Configuração da API
        url = Config.REDCAP_URL
        token = Config.REDCAP_TOKEN
        
        # Obter todos os registros
        print("1️⃣ Obtendo todos os registros...")
        
        records_data = {
            'token': token,
            'content': 'record',
            'format': 'json'
        }
        
        response = requests.post(url, data=records_data, timeout=30)
        
        if response.status_code == 200:
            records = response.json()
            print(f"   ✅ {len(records)} registros obtidos")
            
            if records:
                # Converter para DataFrame
                df = pd.DataFrame(records)
                print(f"   📋 {len(df.columns)} campos totais")
                print(f"   👥 {len(df)} participantes")
                
                # Analisar campos com dados
                fields_with_data = {}
                
                print(f"\n2️⃣ Analisando campos com dados...")
                for col in df.columns:
                    non_null = df[col].notna().sum()
                    non_empty = (df[col] != '').sum()
                    unique_vals = df[col].nunique()
                    
                    if non_null > 0 and non_empty > 0:
                        fields_with_data[col] = {
                            'non_null_count': int(non_null),
                            'non_empty_count': int(non_empty),
                            'unique_values': int(unique_vals),
                            'sample_values': df[col].dropna().head(3).tolist(),
                            'coverage_percent': round((non_empty / len(df)) * 100, 1)
                        }
                
                print(f"   ✅ {len(fields_with_data)} campos com dados válidos")
                
                # Campos mais importantes para análises
                important_categories = {
                    'Demografia': ['age', 'gender', 'marital_status', 'education_level'],
                    'Utilização de Serviços': ['scheduled_medical_visits', 'unscheduled_medical_visits', 'emergency_visits', 'hospitalizations'],
                    'Cuidadores': ['caregiver', 'care_', 'support'],
                    'Medicação': ['medication', 'drug', 'pill', 'adherence'],
                    'Sono': ['sleep', 'sono', 'bed', 'rest'],
                    'Qualidade de Vida': ['quality', 'qol', 'life', 'health'],
                    'Tecnologia': ['technology', 'digital', 'app', 'system']
                }
                
                print(f"\n3️⃣ CAMPOS COM DADOS POR CATEGORIA:")
                useful_fields = {}
                
                for category, keywords in important_categories.items():
                    category_fields = []
                    
                    for field_name, field_info in fields_with_data.items():
                        field_lower = field_name.lower()
                        if any(keyword in field_lower for keyword in keywords):
                            category_fields.append({
                                'field_name': field_name,
                                'coverage': field_info['coverage_percent'],
                                'unique_values': field_info['unique_values'],
                                'samples': field_info['sample_values']
                            })
                    
                    if category_fields:
                        useful_fields[category] = category_fields
                        print(f"\n   📊 {category} ({len(category_fields)} campos):")
                        for field in category_fields[:5]:  # Top 5
                            print(f"     • {field['field_name']}: {field['coverage']}% cobertura, {field['unique_values']} valores únicos")
                            print(f"       Exemplos: {field['samples']}")
                
                # Campos específicos que encontramos
                known_useful_fields = {
                    'scheduled_medical_visits': 'Consultas médicas programadas',
                    'unscheduled_medical_visits': 'Consultas não programadas', 
                    'emergency_visits': 'Visitas ao Serviço de Urgência',
                    'hospitalizations': 'Hospitalizações',
                    'marital_status': 'Estado Civil',
                    'education_level': 'Nível de Educação'
                }
                
                print(f"\n4️⃣ CAMPOS ESPECÍFICOS IDENTIFICADOS:")
                for field, description in known_useful_fields.items():
                    if field in fields_with_data:
                        info = fields_with_data[field]
                        print(f"   ✅ {field}: {description}")
                        print(f"      Cobertura: {info['coverage_percent']}%, Valores únicos: {info['unique_values']}")
                        print(f"      Exemplos: {info['sample_values']}")
                    else:
                        print(f"   ❌ {field}: {description} - SEM DADOS")
                
                # Salvar análise detalhada
                analysis_data = {
                    'total_records': len(df),
                    'total_fields': len(df.columns),
                    'fields_with_data': fields_with_data,
                    'useful_fields_by_category': useful_fields,
                    'known_useful_fields_status': {
                        field: field in fields_with_data for field in known_useful_fields
                    }
                }
                
                with open('detailed_field_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(analysis_data, f, indent=2, ensure_ascii=False)
                
                print(f"\n5️⃣ Análise detalhada salva em 'detailed_field_analysis.json'")
                
                # Resumo para adaptar código
                print(f"\n🎯 RESUMO PARA ADAPTAÇÃO DO CÓDIGO:")
                print(f"   • Total de registros: {len(df)}")
                print(f"   • Campos com dados úteis: {len(fields_with_data)}")
                print(f"   • Principais campos de utilização encontrados: {len([f for f in known_useful_fields if f in fields_with_data])}/{len(known_useful_fields)}")
                
                return df, fields_with_data
                
            else:
                print("   ❌ Nenhum registro encontrado")
                return None, {}
        
        else:
            print(f"   ❌ Erro ao obter registros: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return None, {}
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None, {}

if __name__ == "__main__":
    df, fields_info = get_all_redcap_data()
    
    if df is not None:
        print(f"\n✅ Dados obtidos com sucesso!")
        print(f"   Agora você pode adaptar as análises para usar os campos reais.")
    else:
        print(f"\n❌ Falha ao obter dados.")
