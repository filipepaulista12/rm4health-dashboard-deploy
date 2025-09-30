#!/usr/bin/env python3
"""Script para validar análise de qualidade dos dados"""

from local_redcap_client import LocalREDCapClient
from data_processor import DataProcessor

def validate_data_quality():
    print("=== VALIDAÇÃO ANÁLISE QUALIDADE DADOS ===")
    
    # Carregar dados
    client = LocalREDCapClient()
    records = client.get_records(raw_or_label='raw')
    dp = DataProcessor(records)
    
    print(f"📊 Processando {len(records)} registros...")
    
    try:
        # Testar análise de padrões em falta
        print("\n🔍 Testando análise de padrões em falta...")
        missing_patterns = dp.analyze_missing_patterns()
        print(f"  ✓ Resultados: {type(missing_patterns)} com {len(missing_patterns) if isinstance(missing_patterns, dict) else 'N/A'} elementos")
        
        # Mostrar alguns resultados
        if isinstance(missing_patterns, dict) and missing_patterns:
            for key in list(missing_patterns.keys())[:3]:
                print(f"    - {key}: {missing_patterns[key]}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    try:
        # Testar consistência temporal
        print("\n📅 Testando consistência temporal...")
        consistency_check = dp.check_temporal_consistency()
        print(f"  ✓ Resultados: {type(consistency_check)} com {len(consistency_check) if isinstance(consistency_check, dict) else 'N/A'} elementos")
        
        if isinstance(consistency_check, dict) and consistency_check:
            for key in list(consistency_check.keys())[:3]:
                print(f"    - {key}: {consistency_check[key]}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    try:
        # Testar qualidade de instrumentos
        print("\n📋 Testando qualidade de instrumentos...")
        instrument_quality = dp.assess_instrument_quality()
        print(f"  ✓ Resultados: {type(instrument_quality)} com {len(instrument_quality) if isinstance(instrument_quality, dict) else 'N/A'} elementos")
        
        if isinstance(instrument_quality, dict) and instrument_quality:
            for key in list(instrument_quality.keys())[:3]:
                value = instrument_quality[key]
                if isinstance(value, dict):
                    print(f"    - {key}: {len(value)} sub-elementos")
                else:
                    print(f"    - {key}: {value}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    try:
        # Testar recomendações
        print("\n💡 Testando recomendações de qualidade...")
        recommendations = dp.generate_quality_recommendations()
        print(f"  ✓ Resultados: {type(recommendations)} com {len(recommendations) if isinstance(recommendations, dict) else 'N/A'} elementos")
        
        if isinstance(recommendations, dict) and recommendations:
            for key in list(recommendations.keys())[:3]:
                value = recommendations[key]
                if isinstance(value, list):
                    print(f"    - {key}: {len(value)} recomendações")
                else:
                    print(f"    - {key}: {value}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

if __name__ == "__main__":
    validate_data_quality()